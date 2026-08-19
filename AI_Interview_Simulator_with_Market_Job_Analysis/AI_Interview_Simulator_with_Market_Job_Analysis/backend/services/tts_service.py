"""
Text-to-Speech Service using ElevenLabs API
- Realistic human-like voice
- Emotion control for interviewer tone
- Returns audio bytes for frontend lip sync
"""
import requests
from config import settings

ELEVENLABS_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{settings.ELEVENLABS_VOICE_ID}"

# Emotion → voice settings mapping
# stability: consistency of voice (0-1)
# similarity_boost: adherence to original voice (0-1)
EMOTION_SETTINGS = {
    "neutral": {
        "stability": 0.75,
        "similarity_boost": 0.75,
        "style": 0.0,
        "use_speaker_boost": True
    },
    "confident": {
        "stability": 0.65,
        "similarity_boost": 0.80,
        "style": 0.3,
        "use_speaker_boost": True
    },
    "concerned": {
        "stability": 0.85,
        "similarity_boost": 0.70,
        "style": 0.1,
        "use_speaker_boost": True
    },
    "encouraging": {
        "stability": 0.60,
        "similarity_boost": 0.80,
        "style": 0.4,
        "use_speaker_boost": True
    }
}


def text_to_speech(text: str, emotion: str = "neutral") -> bytes:
    """
    Convert text to speech audio using ElevenLabs API.

    Args:
        text: The text to speak
        emotion: Tone style — neutral / confident / concerned / encouraging

    Returns:
        audio bytes (MP3 format) — send to frontend for lip sync
    """
    voice_settings = EMOTION_SETTINGS.get(emotion, EMOTION_SETTINGS["neutral"])

    headers = {
        "xi-api-key": settings.ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }

    payload = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": voice_settings
    }

    response = requests.post(
        ELEVENLABS_URL,
        headers=headers,
        json=payload,
        timeout=30
    )

    if response.status_code != 200:
        raise Exception(
            f"ElevenLabs API error {response.status_code}: {response.text}"
        )

    return response.content   # raw MP3 bytes


def get_interviewer_emotion(score: float, difficulty: int) -> str:
    """
    Decide what emotion the AI interviewer should use based on performance.
    """
    if score >= 80:
        return "encouraging"
    elif score >= 50:
        return "neutral"
    elif difficulty >= 3:
        return "concerned"
    else:
        return "neutral"
