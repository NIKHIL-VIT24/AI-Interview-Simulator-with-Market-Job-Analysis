from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.sql import func
from database import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    resume_text = Column(Text, nullable=True)
    resume_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, nullable=False)
    session_type = Column(String, default="technical")
    current_difficulty = Column(Integer, default=1)
    questions_asked = Column(JSON, default=[])
    answers_given = Column(JSON, default=[])
    technical_score = Column(Float, nullable=True)
    status = Column(String, default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class BehavioralScore(Base):
    __tablename__ = "behavioral_scores"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, nullable=False)
    speech_rate = Column(Float, nullable=True)
    pause_duration = Column(Float, nullable=True)
    filler_count = Column(Float, nullable=True)
    eye_contact_pct = Column(Float, nullable=True)
    blink_frequency = Column(Float, nullable=True)
    head_movement_var = Column(Float, nullable=True)
    emotion_stability = Column(Float, nullable=True)
    behavioral_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class HiringResult(Base):
    __tablename__ = "hiring_results"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, nullable=False)
    candidate_id = Column(Integer, nullable=False)
    technical_score = Column(Float, nullable=True)
    behavioral_score = Column(Float, nullable=True)
    resume_score = Column(Float, nullable=True)
    hiring_probability = Column(Float, nullable=True)
    recommendation = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
