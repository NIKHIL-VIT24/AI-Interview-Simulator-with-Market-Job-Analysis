"""
Speech-to-Text Service using Faster-Whisper (Small model)
- GPU-efficient (~1GB VRAM)
- Real-time transcription of candidate audio
"""
import torch
import tempfile
import os
try:
    from faster_whisper import WhisperModel
except Exception:
    WhisperModel = None

# Lazy model loading: don't block API startup at import time.
_device = "cuda" if torch.cuda.is_available() else "cpu"
_compute_type = "float16" if _device == "cuda" else "int8"
_whisper_model = None
_whisper_load_error = None


def _get_whisper_model():
    """Load model on first use. Cache either model or load error."""
    global _whisper_model, _whisper_load_error

    if _whisper_model is not None:
        return _whisper_model
    if _whisper_load_error is not None:
        return None
    if WhisperModel is None:
        _whisper_load_error = "faster-whisper is not installed in the current environment."
        return None

    try:
        print(f"[Whisper] Loading model on {_device} with compute_type={_compute_type}")
        _whisper_model = WhisperModel("small", device=_device, compute_type=_compute_type)
        print("[Whisper] Model loaded successfully.")
        return _whisper_model
    except Exception as e:
        _whisper_load_error = str(e)
        print(f"[Whisper] Failed to load model: {_whisper_load_error}")
        return None


def transcribe_audio(audio_bytes: bytes, audio_format: str = "wav") -> dict:
    """
    Transcribe audio bytes to text using Faster-Whisper.

    Args:
        audio_bytes: raw audio file bytes (WAV/MP3/WEBM)
        audio_format: file extension hint

    Returns:
        dict with 'transcript' and 'confidence'
    """
    model = _get_whisper_model()
    if model is None:
        # Keep backend operational even if Whisper model cannot be loaded.
        return {
            "transcript": "",
            "confidence": 0.0,
            "language": "en",
            "duration": 0.0,
        }

    # Write bytes to a temp file
    with tempfile.NamedTemporaryFile(
        suffix=f".{audio_format}", delete=False
    ) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        segments, info = model.transcribe(
            tmp_path,
            language="en",
            beam_size=5,
            vad_filter=True,          # removes silence chunks
            vad_parameters={"min_silence_duration_ms": 300}
        )

        transcript_parts = []
        total_confidence = []

        for seg in segments:
            transcript_parts.append(seg.text.strip())
            # avg_logprob closer to 0 = better; convert to 0-1 confidence
            confidence = min(1.0, max(0.0, 1.0 + seg.avg_logprob))
            total_confidence.append(confidence)

        full_transcript = " ".join(transcript_parts).strip()
        avg_confidence  = (
            sum(total_confidence) / len(total_confidence)
            if total_confidence else 0.0
        )

        return {
            "transcript": full_transcript,
            "confidence": round(avg_confidence, 3),
            "language": info.language,
            "duration": round(info.duration, 2)
        }

    finally:
        os.unlink(tmp_path)  # Clean up temp file

        # Free GPU cache after Whisper (Sequential GPU usage strategy)
        if _device == "cuda":
            torch.cuda.empty_cache()
