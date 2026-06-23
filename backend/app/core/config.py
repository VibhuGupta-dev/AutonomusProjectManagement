import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Autonomous AI Product Manager"
    API_V1_STR: str = "/api/v1"
    GROQ_API_KEY: str = ""
    MAX_UPLOAD_SIZE: int = 20 * 1024 * 1024  # 20MB
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/autonomouspm"
    
    # Clerk Authentication
    CLERK_ISSUER_URL: str = "https://select-trout-29.clerk.accounts.dev"
    CLERK_AUDIENCE: str = "" # Optional depending on config
    
    # AI APIs
    GEMINI_API_KEY: str = ""
    
    UPLOAD_DIR: str = "secure_uploads"
    
    class Config:
        env_file = ".env"

settings = Settings()

# Ensure the secure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
