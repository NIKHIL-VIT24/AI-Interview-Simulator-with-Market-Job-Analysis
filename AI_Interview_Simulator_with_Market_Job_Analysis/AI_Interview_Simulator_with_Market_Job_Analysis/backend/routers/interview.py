"""
Interview Router
- Start/end sessions
- Get adaptive questions
- Submit and evaluate answers
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from services import llama_service, resume_service

router = APIRouter()


@router.post("/start", response_model=schemas.QuestionResponse)
def start_session(req: schemas.StartSessionRequest, db: Session = Depends(get_db)):
    """Start a new interview session and return the first question."""

    # Validate candidate exists
    candidate = db.query(models.Candidate).filter(
        models.Candidate.id == req.candidate_id
    ).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Create a new session
    session = models.InterviewSession(
        candidate_id=req.candidate_id,
        session_type=req.session_type,
        current_difficulty=1,
        questions_asked=[],
        answers_given=[],
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Get candidate skills from resume
    candidate_skills = []
    missing_skills = []
    if candidate.resume_text:
        resume_data   = resume_service.score_resume(candidate.resume_text)
        candidate_skills = resume_data.get("candidate_skills", [])
        missing_skills   = resume_data.get("missing_skills", [])

    # Generate first question
    question = llama_service.generate_question(
        session_type=req.session_type,
        difficulty=1,
        candidate_skills=candidate_skills,
        previous_questions=[],
        missing_skills=missing_skills
    )

    # Save first question
    session.questions_asked = [question]
    db.commit()

    return schemas.QuestionResponse(
        session_id=session.id,
        question=question,
        difficulty=1,
        question_number=1
    )


@router.post("/answer", response_model=schemas.AnswerEvalResponse)
def submit_answer(req: schemas.SubmitAnswerRequest, db: Session = Depends(get_db)):
    """Submit an answer, get evaluation + next question."""

    session = db.query(models.InterviewSession).filter(
        models.InterviewSession.id == req.session_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status == "completed":
        raise HTTPException(status_code=400, detail="Session already completed")

    # Evaluate answer with LLaMA
    evaluation = llama_service.evaluate_answer(
        question=req.question,
        answer=req.answer,
        difficulty=req.difficulty
    )

    score          = evaluation["score"]
    feedback       = evaluation["feedback"]
    next_difficulty = evaluation["next_difficulty"]

    # Update session records
    questions = list(session.questions_asked or [])
    answers   = list(session.answers_given or [])
    answers.append({"question": req.question, "answer": req.answer,
                    "score": score, "difficulty": req.difficulty})
    session.answers_given     = answers
    session.current_difficulty = next_difficulty

    # Get candidate info for next question
    candidate = db.query(models.Candidate).filter(
        models.Candidate.id == session.candidate_id
    ).first()
    candidate_skills = []
    missing_skills   = []
    if candidate and candidate.resume_text:
        resume_data      = resume_service.score_resume(candidate.resume_text)
        candidate_skills = resume_data.get("candidate_skills", [])
        missing_skills   = resume_data.get("missing_skills", [])

    # Generate next question
    next_question = llama_service.generate_question(
        session_type=session.session_type,
        difficulty=next_difficulty,
        candidate_skills=candidate_skills,
        previous_questions=questions,
        missing_skills=missing_skills
    )

    questions.append(next_question)
    session.questions_asked = questions
    db.commit()

    return schemas.AnswerEvalResponse(
        session_id=req.session_id,
        score=score,
        feedback=feedback,
        next_difficulty=next_difficulty,
        next_question=next_question
    )


@router.post("/end/{session_id}")
def end_session(session_id: int, db: Session = Depends(get_db)):
    """Mark a session as completed and compute technical score."""
    session = db.query(models.InterviewSession).filter(
        models.InterviewSession.id == session_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    answers = session.answers_given or []
    scores      = [a["score"] for a in answers]
    difficulties = [a["difficulty"] for a in answers]

    tech_score = llama_service.calculate_technical_score(scores, difficulties)

    session.technical_score = tech_score
    session.status          = "completed"
    db.commit()

    return {
        "session_id": session_id,
        "technical_score": tech_score,
        "total_questions": len(answers),
        "status": "completed"
    }


@router.get("/session/{session_id}")
def get_session(session_id: int, db: Session = Depends(get_db)):
    """Get full session details."""
    session = db.query(models.InterviewSession).filter(
        models.InterviewSession.id == session_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
