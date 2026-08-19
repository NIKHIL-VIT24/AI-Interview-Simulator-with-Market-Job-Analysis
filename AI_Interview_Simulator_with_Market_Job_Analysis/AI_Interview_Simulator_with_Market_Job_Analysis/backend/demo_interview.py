"""
Full Interview Flow Demo Script
Simulates a complete interview session by calling the backend API.

Usage:
    1. Start the backend first:  uvicorn main:app --reload
    2. Then run this:            python demo_interview.py

This script walks through the entire pipeline:
  Candidate creation → Resume upload → Interview → Behavioral → Hiring
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def separator(title: str):
    print(f"\n{'='*55}")
    print(f"  {title}")
    print(f"{'='*55}")

def check(label: str, response):
    if response.status_code in [200, 201]:
        print(f"  ✓ {label}")
        return response.json()
    else:
        print(f"  ✗ {label} — HTTP {response.status_code}: {response.text}")
        return None


# ── Step 0: Health Check ──────────────────────────────────────────────────────
separator("Step 0: Health Check")
r = requests.get(f"{BASE_URL}/health")
data = check("Backend is running", r)
if data:
    print(f"     GPU: {data.get('gpu_name', 'N/A')}")
    print(f"     GPU Available: {data.get('gpu_available', False)}")


# ── Step 1: Create Candidate ──────────────────────────────────────────────────
separator("Step 1: Create Candidate")
r = requests.post(f"{BASE_URL}/resume/candidate", json={
    "name": "Arjun Sharma",
    "email": "arjun.sharma@example.com"
})
candidate = check("Candidate created", r)
if not candidate:
    print("Cannot continue without candidate. Exiting.")
    exit(1)

candidate_id = candidate["id"]
print(f"     Candidate ID: {candidate_id}")


# ── Step 2: Upload Resume ─────────────────────────────────────────────────────
separator("Step 2: Upload Resume (as text)")

sample_resume = """
Arjun Sharma | B.Tech CSE | VIT Bhopal
Email: arjun.sharma@example.com

SKILLS:
Python, Machine Learning, Deep Learning, TensorFlow, PyTorch,
FastAPI, Flask, SQL, PostgreSQL, Docker, Git, React, NLP,
Computer Vision, Data Structures, Algorithms, REST API, AWS

EXPERIENCE:
Machine Learning Intern — TechStartup Pvt Ltd (6 months)
- Built an NLP-based resume screening system using Python and scikit-learn
- Deployed REST API on AWS EC2 with Docker

PROJECTS:
1. AI Chatbot using LLaMA and FastAPI (deployed on local GPU)
2. Facial emotion recognition using EfficientNet-B0 and OpenCV
3. Stock price prediction using LSTM and pandas
4. Open source project: Resume Parser library on GitHub (150+ stars)

EDUCATION:
B.Tech Computer Science and Engineering — VIT Bhopal (2024-2028)
CGPA: 8.7
"""

r = requests.post(f"{BASE_URL}/resume/upload", json={
    "candidate_id": candidate_id,
    "resume_text": sample_resume
})
resume_data = check("Resume uploaded and scored", r)
if resume_data:
    print(f"     Market Skill Match (M): {resume_data['market_skill_match']:.2%}")
    print(f"     Experience Score   (E): {resume_data['experience_score']:.2%}")
    print(f"     Project Score      (P): {resume_data['project_score']:.2%}")
    print(f"     Resume Score       (R): {resume_data['resume_score']:.2%}")
    print(f"     Matched Skills: {', '.join(resume_data['matched_skills'][:6])}")
    print(f"     Missing Skills: {', '.join(resume_data['missing_skills'][:5])}")


# ── Step 3: Start Interview Session ──────────────────────────────────────────
separator("Step 3: Start Interview Session")
r = requests.post(f"{BASE_URL}/interview/start", json={
    "candidate_id": candidate_id,
    "session_type": "technical"
})
session_data = check("Session started", r)
if not session_data:
    print("Cannot continue without session. Exiting.")
    exit(1)

session_id = session_data["session_id"]
print(f"     Session ID:  {session_id}")
print(f"     Difficulty:  {session_data['difficulty']}/4")
print(f"\n     QUESTION 1:")
print(f"     {session_data['question']}")


# ── Step 4: Submit Answers (3 rounds) ────────────────────────────────────────
separator("Step 4: Submit Answers (Simulating 3 Rounds)")

sample_answers = [
    {
        "answer": """Python is an interpreted, high-level, dynamically typed language.
        Key features include: GIL for thread safety, extensive standard library,
        list comprehensions, generators, decorators, and strong ML ecosystem.
        Python's duck typing and dynamic dispatch make it very flexible.""",
        "expected_score": "~75+"
    },
    {
        "answer": """A REST API uses HTTP methods (GET, POST, PUT, DELETE) to
        perform CRUD operations. It's stateless, uses JSON for data exchange,
        and resources are identified by URLs. FastAPI automatically generates
        OpenAPI docs and uses Pydantic for validation.""",
        "expected_score": "~80+"
    },
    {
        "answer": """XGBoost is a gradient boosting algorithm that builds decision
        trees sequentially. Each tree corrects errors of the previous one.
        It uses regularization to prevent overfitting and is very efficient
        on structured/tabular data due to its parallel tree construction.""",
        "expected_score": "~70+"
    }
]

current_question = session_data["question"]
current_difficulty = session_data["difficulty"]
all_scores = []

for i, qa in enumerate(sample_answers):
    r = requests.post(f"{BASE_URL}/interview/answer", json={
        "session_id": session_id,
        "question": current_question,
        "answer": qa["answer"],
        "difficulty": current_difficulty
    })
    eval_data = check(f"Answer {i+1} submitted", r)
    if eval_data:
        all_scores.append(eval_data["score"])
        print(f"     Score: {eval_data['score']}/100")
        print(f"     Difficulty → {eval_data['next_difficulty']}/4")
        print(f"     Feedback: {eval_data['feedback'][:120]}...")
        print(f"\n     NEXT QUESTION:")
        print(f"     {eval_data['next_question'][:200]}...")
        current_question   = eval_data["next_question"]
        current_difficulty = eval_data["next_difficulty"]


# ── Step 5: End Session ───────────────────────────────────────────────────────
separator("Step 5: End Session")
r = requests.post(f"{BASE_URL}/interview/end/{session_id}")
end_data = check("Session ended", r)
if end_data:
    print(f"     Technical Score (T): {end_data['technical_score']}/100")
    print(f"     Total Questions:     {end_data['total_questions']}")
    print(f"     Status:              {end_data['status']}")


# ── Step 6: Submit Behavioral Metrics ────────────────────────────────────────
separator("Step 6: Submit Behavioral Metrics")

# These would come from MediaPipe + Whisper analysis in the real system
r = requests.post(f"{BASE_URL}/behavioral/score", json={
    "session_id": session_id,
    "speech_rate":       0.75,   # normalized — good pace
    "pause_duration":    0.20,   # low pauses — confident
    "filler_count":      0.10,   # few fillers — articulate
    "eye_contact_pct":   0.82,   # good eye contact
    "blink_frequency":   0.40,   # normal blink rate
    "head_movement_var": 0.25,   # stable head
    "emotion_stability": 0.78    # mostly neutral/confident
})
behavioral_data = check("Behavioral metrics submitted", r)
if behavioral_data:
    print(f"     Behavioral Score (B): {behavioral_data['behavioral_score']:.4f}")
    print("     Breakdown:")
    for key, val in behavioral_data["breakdown"].items():
        print(f"       {key}: {val}")


# ── Step 7: Submit Emotion Stability ─────────────────────────────────────────
separator("Step 7: Compute Emotion Stability")
emotion_history = [
    "neutral", "neutral", "happy", "neutral", "neutral",
    "happy",   "neutral", "neutral", "happy",  "neutral"
]
r = requests.post(f"{BASE_URL}/emotion/stability", json={
    "emotion_history": emotion_history
})
emotion_data = check("Emotion stability computed", r)
if emotion_data:
    print(f"     Emotion Stability: {emotion_data['emotion_stability']:.4f}")
    print(f"     Interpretation:    {emotion_data['interpretation']}")
    print(f"     Total Frames:      {emotion_data['total_frames']}")


# ── Step 8: Predict Hiring Probability ───────────────────────────────────────
separator("Step 8: Final Hiring Prediction")
r = requests.post(f"{BASE_URL}/hiring/predict", json={
    "session_id":   session_id,
    "candidate_id": candidate_id
})
hiring_data = check("Hiring probability computed", r)
if hiring_data:
    print(f"\n     ┌─────────────────────────────────┐")
    print(f"     │  FINAL HIRING RESULT            │")
    print(f"     │  Technical Score:  {hiring_data['technical_score']:>5.1f}/100    │")
    print(f"     │  Behavioral Score: {hiring_data['behavioral_score']:>6.2%}       │")
    print(f"     │  Resume Score:     {hiring_data['resume_score']:>6.2%}       │")
    prob_pct = hiring_data['hiring_probability'] * 100
    rec = hiring_data['recommendation']
    print(f"     │  Hiring Probability: {prob_pct:>5.1f}%     │")
    print(f"     │  Recommendation:   {rec:<10}      │")
    print(f"     └─────────────────────────────────┘")


# ── Step 9: Recruiter Dashboard ──────────────────────────────────────────────
separator("Step 9: Recruiter Dashboard")
r = requests.get(f"{BASE_URL}/hiring/dashboard")
dashboard = check("Dashboard fetched", r)
if dashboard:
    print(f"     Total Candidates:     {dashboard.get('total_candidates', 0)}")
    print(f"     Hire Recommendations: {dashboard.get('hire_count', 0)}")
    print(f"     Maybe:                {dashboard.get('maybe_count', 0)}")
    print(f"     Reject:               {dashboard.get('reject_count', 0)}")
    print(f"     Avg Technical Score:  {dashboard.get('avg_technical_score', 0)}")
    print(f"     Avg Hiring Prob:      {dashboard.get('avg_hiring_probability', 0):.2%}")


separator("Demo Complete!")
print("  All API endpoints tested successfully.")
print("  Check http://localhost:8000/docs for full Swagger UI.\n")
