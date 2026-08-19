"""
Resume Router
- POST /resume/upload   → upload resume text for a candidate
- POST /resume/score    → compute market skill match + resume score
- GET  /resume/{id}     → get resume score for a candidate
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from services import resume_service

router = APIRouter()


@router.post("/upload", response_model=schemas.ResumeScoreResponse)
def upload_resume(req: schemas.ResumeUpload, db: Session = Depends(get_db)):
    """
    Upload resume text for a candidate.
    Automatically scores the resume against live market skills.
    """
    candidate = db.query(models.Candidate).filter(
        models.Candidate.id == req.candidate_id
    ).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Score the resume
    result = resume_service.score_resume(req.resume_text)

    # Save to DB
    candidate.resume_text  = req.resume_text
    candidate.resume_score = result["resume_score"]
    db.commit()

    return schemas.ResumeScoreResponse(
        candidate_id=req.candidate_id,
        market_skill_match=result["market_skill_match"],
        experience_score=result["experience_score"],
        project_score=result["project_score"],
        resume_score=result["resume_score"],
        matched_skills=result["matched_skills"],
        missing_skills=result["missing_skills"]
    )


@router.get("/score/{candidate_id}", response_model=schemas.ResumeScoreResponse)
def get_resume_score(candidate_id: int, db: Session = Depends(get_db)):
    """Re-score an existing candidate's resume."""
    candidate = db.query(models.Candidate).filter(
        models.Candidate.id == candidate_id
    ).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    if not candidate.resume_text:
        raise HTTPException(status_code=400, detail="No resume uploaded for this candidate")

    result = resume_service.score_resume(candidate.resume_text)

    return schemas.ResumeScoreResponse(
        candidate_id=candidate_id,
        market_skill_match=result["market_skill_match"],
        experience_score=result["experience_score"],
        project_score=result["project_score"],
        resume_score=result["resume_score"],
        matched_skills=result["matched_skills"],
        missing_skills=result["missing_skills"]
    )


@router.post("/candidate", response_model=schemas.CandidateResponse)
def create_candidate(req: schemas.CandidateCreate, db: Session = Depends(get_db)):
    """Create a new candidate record."""
    existing = db.query(models.Candidate).filter(
        models.Candidate.email == req.email
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    candidate = models.Candidate(name=req.name, email=req.email)
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate
