import re
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from rouge_score import rouge_scorer

from app.rag.engine import rag_engine
from app.logging_config import logger


def calculate_cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    
    try:
        v1 = np.array(vec1).reshape(1, -1)
        v2 = np.array(vec2).reshape(1, -1)
        similarity = cosine_similarity(v1, v2)[0][0]
        return float(np.clip(similarity, 0.0, 1.0))
    except Exception as e:
        logger.error(f"Cosine similarity error: {str(e)}")
        return 0.0


def compute_context_relevance(query: str, contexts: List[str]) -> float:
    
    if not contexts or not query.strip():
        return 0.0

    try:
        query_vector = rag_engine.embed_text(query)
        context_vectors = rag_engine.embed_batch(contexts)

        similarities = [
            calculate_cosine_similarity(query_vector, ctx_vec)
            for ctx_vec in context_vectors
        ]
        return round(float(np.mean(similarities)), 4)
    except Exception as e:
        logger.error(f"Context relevance computation error: {str(e)}")
        return 0.0


def compute_answer_relevance(query: str, answer: str) -> float:
    
    if not answer.strip() or not query.strip():
        return 0.0

    try:
        query_vector = rag_engine.embed_text(query)
        answer_vector = rag_engine.embed_text(answer)
        return round(calculate_cosine_similarity(query_vector, answer_vector), 4)
    except Exception as e:
        logger.error(f"Answer relevance computation error: {str(e)}")
        return 0.0


def compute_faithfulness(answer: str, contexts: List[str]) -> float:
   
    if not contexts or not answer.strip():
        return 0.0

    try:
        
        sentences = [s.strip() for s in re.split(r"[.!?]", answer) if len(s.strip()) > 5]
        if not sentences:
            sentences = [answer.strip()]

        sentence_vectors = rag_engine.embed_batch(sentences)
        context_vectors = rag_engine.embed_batch(contexts)

        sentence_groundedness_scores = []
        for sent_vec in sentence_vectors:
            
            max_sim = max(
                calculate_cosine_similarity(sent_vec, ctx_vec)
                for ctx_vec in context_vectors
            )
            sentence_groundedness_scores.append(max_sim)

        return round(float(np.mean(sentence_groundedness_scores)), 4)
    except Exception as e:
        logger.error(f"Faithfulness computation error: {str(e)}")
        return 0.0


def compute_rouge_scores(generated_answer: str, ground_truth: str) -> Dict[str, float]:
    if not ground_truth or not generated_answer:
        return {"rouge1": 0.0, "rouge2": 0.0, "rougeL": 0.0}

    try:
        scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
        scores = scorer.score(ground_truth, generated_answer)

        return {
            "rouge1": round(scores["rouge1"].fmeasure, 4),
            "rouge2": round(scores["rouge2"].fmeasure, 4),
            "rougeL": round(scores["rougeL"].fmeasure, 4),
        }
    except Exception as e:
        logger.error(f"ROUGE score calculation error: {str(e)}")
        return {"rouge1": 0.0, "rouge2": 0.0, "rougeL": 0.0}
