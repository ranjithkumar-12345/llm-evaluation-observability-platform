import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Settings:
    """All configuration settings"""
    
    # Required - Gemini API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Database
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    
    # Server
    APP_HOST: str = os.getenv("APP_HOST", "127.0.0.1")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
    
    # RAG settings
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "gemini-embedding-2")
    TOP_K_RETRIEVAL: int = int(os.getenv("TOP_K_RETRIEVAL", "5"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

# Create settings object
settings = Settings()

# Check if API key exists
if not settings.GEMINI_API_KEY:
    print(" WARNING: GEMINI_API_KEY not found in .env file")
    print("Please add your API key to continue")