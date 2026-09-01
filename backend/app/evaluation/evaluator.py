import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.databasee import SessionLocal
from app.models import EvaluationLog
from app.rag.engine import rag_engine
from app.evaluation.metrics import (
    compute_context_relevance,
    compute_answer_relevance,
    compute_faithfulness,
    compute_rouge_scores,
)
from app.logging_config import logger


def generate_reasoning(context_rel: float, faithfulness: float, answer_rel: float) -> str:
    
    reasons = []

    if context_rel >= 0.7:
        reasons.append("Retrieved context chunks are highly relevant to the query.")
    elif context_rel >= 0.4:
        reasons.append("Retrieved context contains partial relevance with minor noise.")
    else:
        reasons.append("Retrieved documents have low semantic overlap with the prompt.")

    if faithfulness >= 0.7:
        reasons.append("Generated answer is strongly grounded in the context chunks.")
    elif faithfulness >= 0.4:
        reasons.append("Answer is mostly grounded, but some statements may lack direct context.")
    else:
        reasons.append("Warning: Answer shows potential hallucination or unsupported claims.")

    if answer_rel >= 0.7:
        reasons.append("Answer directly addresses the user's question.")
    else:
        reasons.append("Answer slightly drifts from the core question asked.")

    return " | ".join(reasons)


def evaluate_query(query: str, ground_truth: Optional[str] = None) -> Dict[str, Any]:
    
    try:
        
        rag_output = rag_engine.query_rag(query)
        answer = rag_output.get("answer", "")
        contexts = rag_output.get("contexts", [])
        latency = rag_output.get("latency_seconds", 0.0)

        
        c_rel = compute_context_relevance(query, contexts)
        f_score = compute_faithfulness(answer, contexts)
        a_rel = compute_answer_relevance(query, answer)

        rouge_scores = None
        if ground_truth:
            rouge_scores = compute_rouge_scores(answer, ground_truth)

       
        reasoning = generate_reasoning(c_rel, f_score, a_rel)

       
        serialized_context = json.dumps(contexts)
        with SessionLocal() as db:
            log_entry = EvaluationLog(
                query=query,
                retrieved_context=serialized_context,
                generated_answer=answer,
                context_relevance=c_rel,
                faithfulness=f_score,
                answer_relevance=a_rel,
                reasoning=reasoning,
                latency_seconds=latency,
                timestamp=datetime.utcnow(),
            )
            db.add(log_entry)
            db.commit()
            db.refresh(log_entry)
            log_id = log_entry.id

        logger.info(f"Evaluation completed for query: '{query}' (Log ID: {log_id})")

        return {
            "id": log_id,
            "query": query,
            "answer": answer,
            "contexts": contexts,
            "metrics": {
                "context_relevance": c_rel,
                "faithfulness": f_score,
                "answer_relevance": a_rel,
                "rouge": rouge_scores,
            },
            "reasoning": reasoning,
            "latency_seconds": latency,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error evaluating query '{query}': {str(e)}")
        raise e


def evaluate_batch(test_cases: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    
    results = []
    for test in test_cases:
        query = test.get("query")
        ground_truth = test.get("ground_truth")
        if query:
            res = evaluate_query(query=query, ground_truth=ground_truth)
            results.append(res)
    return results


if __name__ == "__main__":
    test_eval = evaluate_query("What is machine learning?")
    print(json.dumps(test_eval, indent=2))