"""
Behavioral Analytics Router
- POST /behavioral/score  → compute behavioral score from multimodal features
- GET  /behavioral/{session_id}  → get stored behavioral score
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from services import behavioral_service

router = APIRouter()


@router.post("/score", response_model=schemas.BehavioralScoreResponse)
def compute_behavioral(req: schemas.BehavioralInput, db: Session = Depends(get_db)):
    """
    Compute behavioral score from audio/video features.
    The frontend sends these features after each response.
    """
    result = behavioral_service.compute_behavioral_score(
        speech_rate=req.speech_rate,
        pause_duration=req.pause_duration,
        filler_count=req.filler_count,
        eye_contact_pct=req.eye_contact_pct,
        blink_frequency=req.blink_frequency,
        head_movement_var=req.head_movement_var,
        emotion_stability=req.emotion_stability
    )

    # Save to DB
    record = models.BehavioralScore(
        session_id=req.session_id,
        speech_rate=req.speech_rate,
        pause_duration=req.pause_duration,
        filler_count=req.filler_count,
        eye_contact_pct=req.eye_contact_pct,
        blink_frequency=req.blink_frequency,
        head_movement_var=req.head_movement_var,
        emotion_stability=req.emotion_stability,
        behavioral_score=result["behavioral_score"]
    )
    db.add(record)
    db.commit()

    return schemas.BehavioralScoreResponse(
        session_id=req.session_id,
        behavioral_score=result["behavioral_score"],
        breakdown=result["breakdown"]
    )


@router.get("/{session_id}")
def get_behavioral_score(session_id: int, db: Session = Depends(get_db)):
    """Get the latest behavioral score for a session."""
    record = db.query(models.BehavioralScore).filter(
        models.BehavioralScore.session_id == session_id
    ).order_by(models.BehavioralScore.id.desc()).first()

    if not record:
        raise HTTPException(status_code=404, detail="No behavioral score found")

    return record
