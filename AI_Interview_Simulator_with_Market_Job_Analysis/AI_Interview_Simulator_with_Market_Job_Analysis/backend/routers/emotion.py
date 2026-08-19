"""
Emotion Detection Router
- POST /emotion/detect     → single frame emotion detection
- POST /emotion/stability  → compute stability from emotion history
- GET  /emotion/gpu-status → check GPU memory before loading model
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List
from services import emotion_service
from utils.gpu_manager import get_gpu_memory_info

router = APIRouter()


class EmotionHistoryRequest(BaseModel):
    emotion_history: List[str]   # list of emotion strings e.g. ["neutral","happy","neutral"]


@router.post("/detect")
async def detect_emotion(frame: UploadFile = File(...)):
    """
    Detect emotion from a single webcam frame (JPEG/PNG).
    Frontend sends one frame every ~2 seconds during the interview.
    """
    allowed_types = ["image/jpeg", "image/png", "image/webp"]

    frame_bytes = await frame.read()
    if len(frame_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty image frame received")

    try:
        result = emotion_service.detect_emotion_from_frame(frame_bytes)
        return {
            "emotion":    result["emotion"],
            "confidence": result["confidence"],
            "all_scores": result["all_scores"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Emotion detection failed: {str(e)}")


@router.post("/stability")
def compute_stability(req: EmotionHistoryRequest):
    """
    Compute emotion stability score from a list of emotions captured
    throughout the interview session.
    Returns a 0.0 - 1.0 stability score.
    """
    if not req.emotion_history:
        raise HTTPException(status_code=400, detail="Emotion history is empty")

    stability = emotion_service.compute_emotion_stability(req.emotion_history)

    return {
        "emotion_stability": stability,
        "total_frames":      len(req.emotion_history),
        "interpretation": (
            "Highly stable" if stability >= 0.8 else
            "Mostly stable" if stability >= 0.6 else
            "Moderately stable" if stability >= 0.4 else
            "Unstable — high emotional variance"
        )
    }


@router.get("/gpu-status")
def gpu_status():
    """Check GPU memory before loading emotion model."""
    return get_gpu_memory_info()


@router.post("/unload")
def unload_model():
    """
    Unload EfficientNet from GPU after emotion processing is done.
    Call this after the interview session ends to free VRAM.
    """
    emotion_service.unload_emotion_model()
    return {"message": "Emotion model unloaded from GPU successfully"}
