from fastapi import APIRouter
from sqlalchemy import func
import json

from app.databasee import SessionLocal
from app.models import EvaluationLog, DocumentLog

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats():
    
    with SessionLocal() as db:
        total_evals = db.query(func.count(EvaluationLog.id)).scalar() or 0
        total_docs = db.query(func.count(DocumentLog.id)).scalar() or 0

        avg_context = db.query(func.avg(EvaluationLog.context_relevance)).scalar() or 0.0
        avg_faithfulness = db.query(func.avg(EvaluationLog.faithfulness)).scalar() or 0.0
        avg_answer_rel = db.query(func.avg(EvaluationLog.answer_relevance)).scalar() or 0.0
        avg_latency = db.query(func.avg(EvaluationLog.latency_seconds)).scalar() or 0.0

        return {
            "total_documents": total_docs,
            "total_evaluations": total_evals,
            "average_scores": {
                "context_relevance": round(float(avg_context), 4),
                "faithfulness": round(float(avg_faithfulness), 4),
                "answer_relevance": round(float(avg_answer_rel), 4),
            },
            "average_latency_seconds": round(float(avg_latency), 3)
        }


@router.get("/recent-evaluations")
async def get_recent_evaluations(limit: int = 10):
    
    with SessionLocal() as db:
        logs = (
            db.query(EvaluationLog)
            .order_by(EvaluationLog.timestamp.desc())
            .limit(limit)
            .all()
        )

        results = []
        for log in logs:
            try:
                contexts = json.loads(log.retrieved_context) if log.retrieved_context else []
            except Exception:
                contexts = [log.retrieved_context] if log.retrieved_context else []

            results.append({
                "id": log.id,
                "query": log.query,
                "generated_answer": log.generated_answer,
                "contexts": contexts,
                "context_relevance": log.context_relevance,
                "faithfulness": log.faithfulness,
                "answer_relevance": log.answer_relevance,
                "reasoning": log.reasoning,
                "latency_seconds": log.latency_seconds,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None
            })
        return results


@router.get("/metrics-chart")
async def get_metrics_chart_data():
    
    with SessionLocal() as db:
        logs = (
            db.query(EvaluationLog)
            .order_by(EvaluationLog.timestamp.asc())
            .limit(50)
            .all()
        )

        return {
            "timestamps": [log.timestamp.strftime("%H:%M:%S") if log.timestamp else "" for log in logs],
            "context_relevance": [log.context_relevance or 0.0 for log in logs],
            "faithfulness": [log.faithfulness or 0.0 for log in logs],
            "answer_relevance": [log.answer_relevance or 0.0 for log in logs],
            "latency": [log.latency_seconds or 0.0 for log in logs]
        }


