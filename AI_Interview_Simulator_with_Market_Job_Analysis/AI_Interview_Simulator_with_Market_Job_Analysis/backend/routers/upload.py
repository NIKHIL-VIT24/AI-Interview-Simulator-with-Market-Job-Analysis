"""
File Upload Router — for PDF/DOCX resume uploads
Extends the resume router with file upload support.
Add this to main.py: app.include_router(upload.router, prefix="/upload", tags=["Upload"])
"""
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
from services import resume_service
from utils.resume_parser import extract_text_from_file

router = APIRouter()


@router.post("/resume")
async def upload_resume_file(
    candidate_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a PDF or DOCX resume file.
    Extracts text, scores it, and saves to DB.
    """
    candidate = db.query(models.Candidate).filter(
        models.Candidate.id == candidate_id
    ).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Read file bytes
    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty file uploaded")

    # Extract text
    try:
        resume_text = extract_text_from_file(file_bytes, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if len(resume_text.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Could not extract enough text from resume. Try a text-based PDF."
        )

    # Score the resume
    result = resume_service.score_resume(resume_text)

    # Save to DB
    candidate.resume_text  = resume_text
    candidate.resume_score = result["resume_score"]
    db.commit()

    return {
        "candidate_id": candidate_id,
        "filename": file.filename,
        "text_length": len(resume_text),
        "market_skill_match": result["market_skill_match"],
        "experience_score":   result["experience_score"],
        "project_score":      result["project_score"],
        "resume_score":       result["resume_score"],
        "matched_skills":     result["matched_skills"],
        "missing_skills":     result["missing_skills"]
    }
