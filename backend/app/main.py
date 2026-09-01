from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.databasee import Base, engine
from app.logging_config import logger
from app.routes.documents import router as documents_router
from app.routes.evaluation import router as evaluation_router
from app.routes.dashboard import router as dashboard_router


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LLM Evaluation & Observability Platform",
    version="1.0.0",
    description="Automated Evaluation & Observability for RAG Applications"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents_router, prefix="/api/documents", tags=["Documents"])
app.include_router(evaluation_router, prefix="/api/evaluate", tags=["Evaluation"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])


@app.get("/")
async def root():
    return {"message": "LLM Evaluation Platform API is running."}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}