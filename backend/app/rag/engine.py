import time
from typing import List, Dict, Any, Tuple
from google import genai
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.logging_config import logger
from app.database.db_manager import db_manager


class RAGEngine:
    def __init__(self):
        try:
            
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
            self.model_name = "gemini-flash-latest"

            
            logger.info(f"loading embedding model: {settings.EMBEDDING_MODEL}")
            self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.info("RAG_Engine has successfully initialized")
        except Exception as e:
            logger.error("Failed to initialize RAG_Engine")
            raise e

    def embed_text(self, text: str) -> List[float]:
        try:
            embedding = self.embedding_model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"embedding text error: {str(e)}")
            raise e

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        try:
            embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
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

    def generate_answer(self, query: str, contexts: List[str]) -> str:
        try:
            context_block = "\n\n".join(
                [f"[Context {i+1}]: {ctx}" for i, ctx in enumerate(contexts)]
            )

            prompt = (
                "You are an accurate, helpful AI assistant. Answer the user's question "
                "strictly using the provided context information below. If the answer cannot "
                "be derived from the context, clearly state that the information is unavailable.\n\n"
                f"--- CONTEXT ---\n{context_block}\n\n"
                f"--- QUESTION ---\n{query}\n\n"
                "--- ANSWER ---"
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text.strip() if response.text else "No response generated."
        except Exception as e:
            logger.error(f"Error generating answer from Gemini: {str(e)}")
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