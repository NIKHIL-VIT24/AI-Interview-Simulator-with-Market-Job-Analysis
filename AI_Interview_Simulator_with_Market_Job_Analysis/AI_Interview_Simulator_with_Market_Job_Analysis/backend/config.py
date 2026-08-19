from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # PostgreSQL — change these to match your local DB setup
    DATABASE_URL = "sqlite:///./ai_interview.db"

    # ElevenLabs TTS API key
    ELEVENLABS_API_KEY: str = "your_elevenlabs_api_key_here"
    ELEVENLABS_VOICE_ID: str = "your_voice_id_here"

    # LLaMA via Ollama (runs locally)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLAMA_MODEL: str = "llama3:8b-instruct-q4_0"

    # Job Market API (Adzuna)
    ADZUNA_APP_ID: str = "your_adzuna_app_id"
    ADZUNA_API_KEY: str = "your_adzuna_api_key"

    class Config:
        env_file = ".env"

settings = Settings()
