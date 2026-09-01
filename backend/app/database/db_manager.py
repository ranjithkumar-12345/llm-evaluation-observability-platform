import chromadb
from app.config import settings
from app.logging_config import logger
from dotenv import load_dotenv
from typing import List,Dict,Any

load_dotenv

class ChromaDBManager():
    def __init__(self):

        try:
            self.client = chromadb.PersistentClient(path = settings.CHROMA_PERSIST_DIR)

            self.collection = self.client.get_or_create_collection(
                name = "rag_documents",

                metadata = {"hnsw:space":"cosine"}
                )
            logger.info("Chromadb is intialized and rag_documents is ready") 

        except Exception as e:
            logger.error(f"failed to intialized chromadb:{str(e)}")
            raise e
    

    def add_documents(self,documents,embeddings):

        try:
            ids = [doc[id] for doc in documents]

            contents = [doc["content"] for doc in documents]

            metadatas = [doc.get("metadata",{}) for doc in documents]

            self.collection.add(
                ids=ids,
                embeddings = embeddings,
                documents=contents,
                metadatas= metadatas
                )

            logger.info(f"Successfully installed {len(ids)} document chunks in Chromadb.")

        except Exception as e:
            logger.error(f"error adding documents in chromadb:{str(e)}")

            raise e


    def query(self,query_embedding:List[float],top_k:int=5)->Dict[str,Any]:

        try:
            results = self.collection.query(
                query_embeddings = [query_embedding],
                n_results = top_k

                )
            logger.info(f"Query returned {len(results.get('documents', [[]])[0])} matching chunks.")
            return results

        except Exception as e:
            logger.error(f"Error querying ChromaDB: {str(e)}")
            raise e

    def delete_documents(self,doc_id):

        try:
            self.collection.delete(ids=[doc_id])
            logger.info(f"Deleted document with ID: {doc_id} from ChromaDB.")

        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {str(e)}")
            raise e

    def get_all_documents(self)->Dict[List,Any]:

        try:
            return self.collection.get()
        
        except Exception as e:
            logger.error(f"Error fetching all documents from ChromaDB: {str(e)}")
            raise e

db_manager = ChromaDBManager()

if __name__ =="__main__":
    print(db_manager)