"""
Hiring Probability Router
- POST /hiring/predict  → compute final hiring probability
- GET  /hiring/results/{candidate_id}  → get all results for a candidate
- GET  /hiring/dashboard  → recruiter dashboard data
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from services import hiring_service

router = APIRouter()


@router.post("/predict", response_model=schemas.HiringResponse)
def predict_hiring(req: schemas.HiringRequest, db: Session = Depends(get_db)):
    """
    Compute final hiring probability for a completed session.
    Combines technical, behavioral, and resume scores via XGBoost model.
    """
    # Fetch session
    session = db.query(models.InterviewSession).filter(
        models.InterviewSession.id == req.session_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Fetch candidate
    candidate = db.query(models.Candidate).filter(
        models.Candidate.id == req.candidate_id
    ).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Fetch behavioral score
    behavioral = db.query(models.BehavioralScore).filter(
        models.BehavioralScore.session_id == req.session_id
    ).order_by(models.BehavioralScore.id.desc()).first()

    # Collect scores
    tech_score       = session.technical_score or 50.0
    behavioral_score = behavioral.behavioral_score if behavioral else 0.5
    resume_score     = candidate.resume_score or 0.3

    # Max difficulty reached
    answers       = session.answers_given or []
    max_difficulty = max((a.get("difficulty", 1) for a in answers), default=1)

    # Eye contact and speech rate from behavioral record
    eye_contact   = behavioral.eye_contact_pct if behavioral else 0.5
    speech_rate   = behavioral.speech_rate if behavioral else 0.5

    # Predict
    result = hiring_service.predict_hiring_probability(
        technical_score=tech_score,
        behavioral_score=behavioral_score,
        resume_score=resume_score,
        max_difficulty=max_difficulty,
        eye_contact_pct=eye_contact,
        speech_rate_norm=speech_rate
    )

    # Save result
    hiring_record = models.HiringResult(
        session_id=req.session_id,
        candidate_id=req.candidate_id,
        technical_score=tech_score,
        behavioral_score=behavioral_score,
        resume_score=resume_score,
        hiring_probability=result["hiring_probability"],
        recommendation=result["recommendation"]
    )
    db.add(hiring_record)
    db.commit()

    return schemas.HiringResponse(
        session_id=req.session_id,
        candidate_id=req.candidate_id,
        technical_score=tech_score,
        behavioral_score=behavioral_score,
        resume_score=resume_score,
        hiring_probability=result["hiring_probability"],
        recommendation=result["recommendation"]
    )


@router.get("/dashboard")
def recruiter_dashboard(db: Session = Depends(get_db)):
    """Recruiter analytics dashboard — aggregated results."""
    results = db.query(models.HiringResult).all()

    if not results:
        return {"message": "No hiring results yet", "candidates": []}

    total = len(results)
    hired = sum(1 for r in results if r.recommendation == "Hire")
    maybe = sum(1 for r in results if r.recommendation == "Maybe")
    reject= sum(1 for r in results if r.recommendation == "Reject")

    avg_tech      = sum(r.technical_score   for r in results) / total
    avg_behavioral= sum(r.behavioral_score  for r in results) / total
    avg_prob      = sum(r.hiring_probability for r in results) / total

    return {
        "total_candidates": total,
        "hire_count": hired,
        "maybe_count": maybe,
        "reject_count": reject,
        "avg_technical_score": round(avg_tech, 2),
        "avg_behavioral_score": round(avg_behavioral, 4),
        "avg_hiring_probability": round(avg_prob, 4),
        "candidates": [
            {
                "candidate_id": r.candidate_id,
                "session_id": r.session_id,
                "technical_score": r.technical_score,
                "behavioral_score": r.behavioral_score,
                "resume_score": r.resume_score,
                "hiring_probability": r.hiring_probability,
                "recommendation": r.recommendation,
                "created_at": str(r.created_at)
            }
            for r in results
        ]
    }
