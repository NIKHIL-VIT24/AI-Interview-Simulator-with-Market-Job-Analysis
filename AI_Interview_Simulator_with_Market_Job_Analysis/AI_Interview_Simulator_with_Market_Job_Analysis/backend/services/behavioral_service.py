"""
Behavioral Analytics Service
Computes Behavioral Score (B) from multimodal features:
  - Audio: speech rate, pause duration, filler word count
  - Video: eye contact %, blink frequency, head movement variance
  - Emotion: stability index

Formula (from architecture doc):
  B = 0.2*SR + 0.15*(1-PD) + 0.15*(1-FC) + 0.2*EC + 0.15*(1-BMvar) + 0.15*ES
"""


def compute_behavioral_score(
    speech_rate: float,       # normalized words/min (0-1 scale)
    pause_duration: float,    # normalized avg pause duration (0-1)
    filler_count: float,      # normalized filler word frequency (0-1)
    eye_contact_pct: float,   # 0.0 to 1.0
    blink_frequency: float,   # normalized blink rate (0-1)
    head_movement_var: float, # normalized head movement variance (0-1)
    emotion_stability: float  # 0.0 to 1.0
) -> dict:
    """
    Compute weighted Behavioral Score B.

    All inputs should be normalized to 0.0 - 1.0 range.
    Lower pause_duration, filler_count, head_movement_var = better.
    Higher speech_rate (moderate), eye_contact, emotion_stability = better.
    """

    # Clamp all values to [0, 1]
    def clamp(v): return max(0.0, min(1.0, v))

    SR    = clamp(speech_rate)
    PD    = clamp(pause_duration)
    FC    = clamp(filler_count)
    EC    = clamp(eye_contact_pct)
    BM    = clamp(head_movement_var)
    ES    = clamp(emotion_stability)

    # B formula
    B = (
        0.20 * SR +
        0.15 * (1 - PD) +
        0.15 * (1 - FC) +
        0.20 * EC +
        0.15 * (1 - BM) +
        0.15 * ES
    )

    breakdown = {
        "speech_rate_contribution":       round(0.20 * SR, 4),
        "pause_duration_contribution":    round(0.15 * (1 - PD), 4),
        "filler_count_contribution":      round(0.15 * (1 - FC), 4),
        "eye_contact_contribution":       round(0.20 * EC, 4),
        "head_movement_contribution":     round(0.15 * (1 - BM), 4),
        "emotion_stability_contribution": round(0.15 * ES, 4),
    }

    return {
        "behavioral_score": round(B, 4),
        "breakdown": breakdown,
        "interpretation": interpret_behavioral_score(B)
    }


def interpret_behavioral_score(score: float) -> str:
    if score >= 0.80:
        return "Excellent — Highly confident and composed"
    elif score >= 0.65:
        return "Good — Generally confident with minor areas to improve"
    elif score >= 0.50:
        return "Average — Some behavioral weaknesses detected"
    else:
        return "Needs Improvement — Significant behavioral concerns"


def normalize_speech_rate(words_per_minute: float) -> float:
    """
    Normalize speech rate: ideal range is ~120-160 wpm
    - Too slow (<80 wpm) or too fast (>200 wpm) scores lower
    """
    if 120 <= words_per_minute <= 160:
        return 1.0
    elif words_per_minute < 80 or words_per_minute > 220:
        return 0.3
    elif words_per_minute < 120:
        return 0.5 + (words_per_minute - 80) / (120 - 80) * 0.5
    else:
        return 1.0 - (words_per_minute - 160) / (220 - 160) * 0.7


def count_filler_words(transcript: str) -> int:
    """Count filler words in a transcript."""
    fillers = [
        "um", "uh", "like", "you know", "sort of", "kind of",
        "basically", "literally", "actually", "so", "right",
        "hmm", "ah", "er"
    ]
    text_lower = transcript.lower()
    count = 0
    for filler in fillers:
        count += text_lower.split().count(filler)
    return count


def normalize_filler_count(filler_count: int, total_words: int) -> float:
    """Normalize filler count as a ratio of total words spoken."""
    if total_words == 0:
        return 0.0
    ratio = filler_count / total_words
    # More than 10% fillers = score 1.0 (bad), 0% = score 0.0 (perfect)
    return min(1.0, ratio / 0.10)
