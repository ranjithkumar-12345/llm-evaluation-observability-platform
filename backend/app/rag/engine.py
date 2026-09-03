import time
from typing import List, Dict, Any, Tuple
from google import genai

from app.config import settings
from app.logging_config import logger
from app.database.db_manager import db_manager


class RAGEngine:
    def __init__(self):
        try:
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
            self.model_name = "gemini-3.6-flash"
            self.embedding_model_name = "text-embedding-004"

            logger.info(f"RAG_Engine initialized using lightweight API embeddings: {self.embedding_model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize RAG_Engine: {str(e)}")
            raise e

    def embed_text(self, text: str) -> List[float]:
        try:
            response = self.client.models.embed_content(
                model=self.embedding_model_name,
                contents=text
            )
            return response.embedding.values
        except Exception as e:
            logger.error(f"embedding text error: {str(e)}")
            raise e

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        try:
            embeddings = []
            for t in texts:
                emb = self.embed_text(t)
                embeddings.append(emb)
            return embeddings
        except Exception as e:
            logger.error(f"embedding batch error: {str(e)}")
            raise e

    def retrieve_context(self, query: str, top_k: int = None) -> Tuple[List[str], List[Dict[str, Any]], List[float]]:
        k = top_k or settings.TOP_K_RETRIEVAL
        try:
            query_vector = self.embed_text(query)
            query_results = db_manager.query(query_embedding=query_vector, top_k=k)

            documents = query_results.get("documents", [[]])[0]
            metadatas = query_results.get("metadatas", [[]])[0]
            distances = query_results.get("distances", [[]])[0]

            return documents, metadatas, distances
        except Exception as e:
            logger.error(f"Error retrieving context for query '{query}': {str(e)}")
            raise e

    def generate_answer(self, query: str, context: list) -> str:
        prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                return response.text
            except Exception as e:
                err_str = str(e)
                if ("503" in err_str or "11001" in err_str) and attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                raise e

    def query_rag(self, query: str, top_k: int = None) -> Dict[str, Any]:
        start_time = time.time()
        try:
            contexts, metadatas, distances = self.retrieve_context(query, top_k)

            if not contexts:
                answer = "No relevant context found in the database to answer this question."
            else:
                answer = self.generate_answer(query, contexts)

            latency = round(time.time() - start_time, 3)

            return {
                "query": query,
                "answer": answer,
                "contexts": contexts,
                "metadatas": metadatas,
                "distances": distances,
                "latency_seconds": latency
            }
        except Exception as e:
            logger.error(f"RAG query execution failed: {str(e)}")
            raise e


rag_engine = RAGEngine()

if __name__ == "__main__":
    print(rag_engine)