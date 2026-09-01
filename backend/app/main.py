from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.logging_config import logger

# Create FastAPI app
app = FastAPI(
    title="LLM Evaluation Platform",
    description="Evaluate RAG system quality",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    logger.info("Root endpoint called")
    return {
        "message": "LLM Evaluation Platform",
        "status": "running"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

logger.info("Application started successfully!")