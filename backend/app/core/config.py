import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "DocuMind RAG Assistant API"
    UPLOAD_DIR: str = "./uploaded_files"
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)