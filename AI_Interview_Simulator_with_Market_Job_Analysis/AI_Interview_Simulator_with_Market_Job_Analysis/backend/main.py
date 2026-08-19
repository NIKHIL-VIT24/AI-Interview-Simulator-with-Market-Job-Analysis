from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import interview, resume, behavioral, hiring, speech, upload, emotion
from database import engine, Base

# Create all DB tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Market-Aware Adaptive Interviewing AI",
    description="Backend API for AI Interview Simulator",
    version="1.0.0"
)

# Allow frontend (React) to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
app.include_router(interview.router, prefix="/interview", tags=["Interview"])
app.include_router(resume.router,    prefix="/resume",    tags=["Resume"])
app.include_router(behavioral.router,prefix="/behavioral",tags=["Behavioral"])
app.include_router(hiring.router,    prefix="/hiring",    tags=["Hiring"])
app.include_router(speech.router,     prefix="/speech",     tags=["Speech"])
app.include_router(upload.router,     prefix="/upload",     tags=["Upload"])
app.include_router(emotion.router,    prefix="/emotion",    tags=["Emotion"])

@app.get("/health")
def health():
    """Health check — confirms GPU availability."""
    import torch
    return {
        "status": "ok",
        "gpu_available": torch.cuda.is_available(),
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU only"
    }

@app.get("/")
def root():
    return {"message": "AI Interview Backend is running!"}
