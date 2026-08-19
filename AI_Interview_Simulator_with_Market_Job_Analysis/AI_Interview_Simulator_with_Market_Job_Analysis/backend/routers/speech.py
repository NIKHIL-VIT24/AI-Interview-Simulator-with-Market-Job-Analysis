"""
Speech Router
- POST /speech/stt  → audio file → transcript
- POST /speech/tts  → text → audio bytes (MP3)
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response
import schemas
from services import whisper_service, tts_service

router = APIRouter()


@router.post("/stt", response_model=schemas.STTResponse)
async def speech_to_text(audio: UploadFile = File(...)):
    """
    Transcribe uploaded audio file using Faster-Whisper.
    Accepts: WAV, MP3, WEBM (browser MediaRecorder output)
    """
    allowed_types = ["audio/wav", "audio/mpeg", "audio/webm", "audio/ogg"]

    # Read audio bytes
    audio_bytes = await audio.read()

    if len(audio_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty audio file")

    # Determine format from filename
    filename = audio.filename or "audio.wav"
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext not in ["wav", "mp3", "webm", "ogg", "m4a"]:
        ext = "wav"

    result = whisper_service.transcribe_audio(audio_bytes, audio_format=ext)

    return schemas.STTResponse(
        transcript=result["transcript"],
        confidence=result["confidence"]
    )


@router.post("/tts")
def text_to_speech(req: schemas.TTSRequest):
    """
    Convert text to speech audio using ElevenLabs.
    Returns MP3 audio bytes — frontend uses this for avatar lip sync.
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        audio_bytes = tts_service.text_to_speech(
            text=req.text,
            emotion=req.emotion
        )
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={"Content-Disposition": "inline; filename=speech.mp3"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
