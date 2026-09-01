from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from app.evaluation.evaluator import evaluate_query, evaluate_batch
from app.logging_config import logger

router = APIRouter()


class SingleQueryRequest(BaseModel):
    query: str
    ground_truth: Optional[str] = None


class BatchQueryItem(BaseModel):
    query: str
    ground_truth: Optional[str] = None


class BatchQueryRequest(BaseModel):
    test_cases: List[BatchQueryItem]


@router.post("/query")
async def evaluate_single_query(payload: SingleQueryRequest):
    
    try:
        result = evaluate_query(query=payload.query, ground_truth=payload.ground_truth)
        return result
    except Exception as e:
        logger.error(f"Error evaluating single query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch")
async def evaluate_batch_queries(payload: BatchQueryRequest):
    
    try:
        raw_test_cases = [item.model_dump() for item in payload.test_cases]
        results = evaluate_batch(test_cases=raw_test_cases)
        return {"total_evaluated": len(results), "results": results}
    except Exception as e:
        logger.error(f"Error in batch evaluation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_available_metrics():
    
    return {
        "metrics": [
            {
                "name": "Context Relevance",
                "range": "0.0 - 1.0",
                "description": "Measures similarity between query and retrieved document chunks."
            },
            {
                "name": "Faithfulness",
                "range": "0.0 - 1.0",
                "description": "Measures whether the answer is grounded in retrieved context (hallucination detection)."
            },
            {
                "name": "Answer Relevance",
                "range": "0.0 - 1.0",
                "description": "Measures whether the answer directly answers the query."
            },
            {
                "name": "ROUGE-L",
                "range": "0.0 - 1.0",
                "description": "Measures overlap with ground truth reference if provided."
            }
        ]
    }