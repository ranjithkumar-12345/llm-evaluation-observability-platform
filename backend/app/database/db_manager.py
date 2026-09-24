import chromadb
from app.config import settings
from app.logging_config import logger
from dotenv import load_dotenv
from typing import List, Dict, Any

load_dotenv()


class ChromaDBManager:

    def __init__(self):

        try:
            self.client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIR
            )

            self.client.delete_collection(name="rag_documents")

            self.collection = self.client.get_or_create_collection(
                name="rag_documents",
                metadata={"hnsw:space": "cosine"}
            )

            logger.info(
                "ChromaDB is initialized and rag_documents is ready"
            )

        except Exception as e:

            logger.exception(
                f"Failed to initialize ChromaDB: {e}"
            )

            raise

    # --------------------------------------------------
    # ADD DOCUMENTS
    # --------------------------------------------------

    def add_documents(
        self,
        ids,
        documents,
        embeddings,
        metadatas
    ):

        try:

            # Validate lengths
            if not (
                len(ids)
                == len(documents)
                == len(embeddings)
                == len(metadatas)
            ):
                raise ValueError(
                    "ids, documents, embeddings and metadatas "
                    "must have the same length."
                )

            self.collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas
            )

            logger.info(
                f"Successfully installed "
                f"{len(ids)} document chunks in ChromaDB."
            )

        except Exception as e:

            logger.exception(
                f"Error adding documents in ChromaDB: {e}"
            )

            raise

    # --------------------------------------------------
    # QUERY
    # --------------------------------------------------

    def query(
        self,
        query_embedding: List[float],
        top_k: int = 5
    ) -> Dict[str, Any]:

        try:

            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )

            logger.info(
                f"Query returned "
                f"{len(results.get('documents', [[]])[0])} "
                f"matching chunks."
            )

            return results

        except Exception as e:

            logger.exception(
                f"Error querying ChromaDB: {e}"
            )

            raise

    # --------------------------------------------------
    # DELETE DOCUMENT CHUNKS
    # --------------------------------------------------

    def delete_documents_by_doc_id(
        self,
        doc_id: str
    ):

        try:

            self.collection.delete(
                where={
                    "doc_id": doc_id
                }
            )

            logger.info(
                f"Deleted all chunks for document "
                f"{doc_id} from ChromaDB."
            )

        except Exception as e:

            logger.exception(
                f"Error deleting document {doc_id}: {e}"
            )

            raise

    # --------------------------------------------------
    # GET ALL DOCUMENTS
    # --------------------------------------------------

    def get_all_documents(self) -> Dict[str, Any]:

        try:

            return self.collection.get()

        except Exception as e:

            logger.exception(
                f"Error fetching all documents "
                f"from ChromaDB: {e}"
            )

            raise


# --------------------------------------------------
# CREATE DATABASE MANAGER
# --------------------------------------------------

db_manager = ChromaDBManager()


if __name__ == "__main__":
    print(db_manager)