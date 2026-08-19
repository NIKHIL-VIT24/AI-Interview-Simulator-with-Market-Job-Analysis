# Market-Aware Adaptive Interviewing AI — Backend

Full Python/FastAPI backend for the AI Interview Simulator.

---

## Project Structure

```
backend/
│
├── main.py                        ← FastAPI app entry point
├── config.py                      ← All settings & API keys
├── database.py                    ← PostgreSQL connection
├── models.py                      ← Database table definitions
├── schemas.py                     ← Request/Response data shapes
├── requirements.txt               ← All Python dependencies
├── .env.example                   ← Copy this to .env and fill in keys
│
├── routers/                       ← API endpoint files
│   ├── interview.py               ← Start session, submit answers
│   ├── resume.py                  ← Create candidate, upload resume text
│   ├── upload.py                  ← Upload PDF/DOCX resume files
│   ├── speech.py                  ← STT (Whisper) + TTS (ElevenLabs)
│   ├── behavioral.py              ← Submit behavioral metrics
│   └── hiring.py                  ← Predict hiring probability, dashboard
│
├── services/                      ← Core AI/ML logic
│   ├── llama_service.py           ← LLaMA adaptive questions + evaluation
│   ├── whisper_service.py         ← Faster-Whisper speech-to-text
│   ├── tts_service.py             ← ElevenLabs text-to-speech
│   ├── resume_service.py          ← Market skill match + resume scoring
│   ├── behavioral_service.py      ← Behavioral score formula
│   ├── emotion_service.py         ← EfficientNet-B0 emotion detection
│   └── hiring_service.py          ← XGBoost hiring probability model
│
├── utils/
│   ├── gpu_manager.py             ← Sequential GPU usage (RTX 3050 safe)
│   └── resume_parser.py           ← PDF/DOCX text extraction
│
└── models/                        ← Saved ML model weights
    └── hiring_model.pkl           ← Auto-created on first run
```

---

## Step-by-Step Setup

### 1. Install PostgreSQL
Download from https://www.postgresql.org/download/
- Create a database called `ai_interview_db`
- Note your username and password

### 2. Install Ollama + LLaMA 3
```bash
# Download Ollama from https://ollama.com
# Then pull the model:
ollama pull llama3:8b-instruct-q4_0
# Start Ollama server:
ollama serve
```

### 3. Set Up Python Environment
```bash
# In the backend/ folder:
python -m venv venv

# Activate (Windows):
venv\Scripts\activate

# Activate (Mac/Linux):
source venv/bin/activate

# Install all packages:
pip install -r requirements.txt
```

### 4. Create Your .env File
```bash
# Copy the example:
cp .env.example .env

# Edit .env and fill in:
# - DATABASE_URL  (your PostgreSQL password)
# - ELEVENLABS_API_KEY  (from elevenlabs.io)
# - ELEVENLABS_VOICE_ID
# - ADZUNA_APP_ID + ADZUNA_API_KEY  (from developer.adzuna.com — free)
```

### 5. Run the Backend
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Test It
Open in browser: http://localhost:8000/docs
This shows the interactive Swagger UI for all your API endpoints.

---

## API Endpoints Quick Reference

| Method | Endpoint                    | What it does                          |
|--------|-----------------------------|---------------------------------------|
| POST   | /resume/candidate           | Create a new candidate                |
| POST   | /upload/resume              | Upload PDF/DOCX resume                |
| POST   | /interview/start            | Start interview, get first question   |
| POST   | /interview/answer           | Submit answer, get score + next Q     |
| POST   | /interview/end/{session_id} | End session, compute tech score       |
| POST   | /speech/stt                 | Audio → transcript (Whisper)          |
| POST   | /speech/tts                 | Text → audio MP3 (ElevenLabs)         |
| POST   | /behavioral/score           | Submit behavioral metrics             |
| POST   | /hiring/predict             | Compute final hiring probability      |
| GET    | /hiring/dashboard           | Recruiter analytics dashboard         |
| GET    | /health                     | Check GPU status                      |

---

## Typical Interview Flow

```
1. POST /resume/candidate        → get candidate_id
2. POST /upload/resume           → upload resume, get skills
3. POST /interview/start         → get session_id + first question
4. POST /speech/tts              → convert question to audio (avatar speaks)
5. (Candidate answers via mic)
6. POST /speech/stt              → audio → transcript
7. POST /interview/answer        → evaluate answer, get next question
8. (Repeat steps 4-7 for N questions)
9. POST /interview/end/{id}      → compute technical score
10. POST /behavioral/score       → submit video/audio metrics
11. POST /hiring/predict         → get final Hiring Probability
12. GET  /hiring/dashboard       → recruiter sees all results
```

---

## GPU Memory Notes (RTX 3050 — 4GB VRAM)

Models are NEVER loaded simultaneously. The backend uses sequential loading:
- Whisper runs → cache cleared → LLaMA runs → cache cleared → EfficientNet runs
- This is handled automatically via `utils/gpu_manager.py`

---

## Notes for Team

- **Payal (Backend)**: All files above are yours to implement
- **Frontend team**: Connect to `http://localhost:8000` — CORS is already enabled for `localhost:3000`
- **EfficientNet weights**: You need to train on FER2013 dataset and save to `models/efficientnet_emotion.pth`
- **XGBoost**: Currently uses LogisticRegression as fallback; switches to XGBoost automatically once you call `retrain_with_real_data()`
