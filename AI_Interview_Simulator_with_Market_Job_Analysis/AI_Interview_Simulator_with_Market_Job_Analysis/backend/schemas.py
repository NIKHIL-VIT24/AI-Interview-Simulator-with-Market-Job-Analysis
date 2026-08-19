from pydantic import BaseModel
from typing import Optional, List

# ── Candidate ──────────────────────────────────────────────
class CandidateCreate(BaseModel):
    name: str
    email: str

class CandidateResponse(BaseModel):
    id: int
    name: str
    email: str
    resume_score: Optional[float] = None

    class Config:
        from_attributes = True


# ── Resume ─────────────────────────────────────────────────
class ResumeUpload(BaseModel):
    candidate_id: int
    resume_text: str          # extracted text from PDF/DOCX

class ResumeScoreResponse(BaseModel):
    candidate_id: int
    market_skill_match: float  # M
    experience_score: float    # E
    project_score: float       # P
    resume_score: float        # R = 0.4M + 0.3E + 0.3P
    matched_skills: List[str]
    missing_skills: List[str]


# ── Interview ──────────────────────────────────────────────
class StartSessionRequest(BaseModel):
    candidate_id: int
    session_type: str = "technical"   # technical / hr / mixed

class QuestionResponse(BaseModel):
    session_id: int
    question: str
    difficulty: int
    question_number: int

class SubmitAnswerRequest(BaseModel):
    session_id: int
    question: str
    answer: str
    difficulty: int

class AnswerEvalResponse(BaseModel):
    session_id: int
    score: float              # 0–100 for this answer
    feedback: str
    next_difficulty: int
    next_question: str


# ── Speech ────────────────────────────────────────────────
class TTSRequest(BaseModel):
    text: str
    emotion: str = "neutral"  # neutral / confident / concerned

class STTResponse(BaseModel):
    transcript: str
    confidence: float


# ── Behavioral ────────────────────────────────────────────
class BehavioralInput(BaseModel):
    session_id: int
    speech_rate: float
    pause_duration: float
    filler_count: float
    eye_contact_pct: float
    blink_frequency: float
    head_movement_var: float
    emotion_stability: float

class BehavioralScoreResponse(BaseModel):
    session_id: int
    behavioral_score: float
    breakdown: dict           # individual weighted contributions


# ── Hiring ────────────────────────────────────────────────
class HiringRequest(BaseModel):
    session_id: int
    candidate_id: int

class HiringResponse(BaseModel):
    session_id: int
    candidate_id: int
    technical_score: float
    behavioral_score: float
    resume_score: float
    hiring_probability: float
    recommendation: str       # Hire / Maybe / Reject
