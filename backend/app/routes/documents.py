import io
import uuid
from typing import List
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, HTTPException
import PyPDF2
from docx import Document
from app.databasee import SessionLocal
from app.database.db_manager import db_manager
from app.models import DocumentLog
from app.rag.engine import rag_engine
from app.logging_config import logger

router = APIRouter()


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50
) -> List[str]:
    """Splits raw text into sliding window chunks with overlap."""

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Accepts PDF or TXT files, extracts text, chunks it,
    generates embeddings, and saves them to ChromaDB.
    """

    filename = file.filename or ""
    content = await file.read()
    raw_text = ""

    try:

        # -----------------------------------------
        # 1. Check file type
        # -----------------------------------------
        if filename.lower().endswith(".pdf"):

            pdf_reader = PyPDF2.PdfReader(
                io.BytesIO(content)
            )

            for page in pdf_reader.pages:
                extracted = page.extract_text()

                if extracted:
                    raw_text += extracted + "\n"
                    
        elif filename.lower().endswith(".docx"):
        
            doc = Document(
                io.BytesIO(content)
            )
        
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    raw_text += paragraph.text + "\n"       

        elif filename.lower().endswith(".txt"):

            raw_text = content.decode("utf-8")

        else:
            raise HTTPException(
                status_code=400,
                detail="Only .pdf and .txt files are supported."
            )

        # -----------------------------------------
        # 2. Check extracted text
        # -----------------------------------------
        if not raw_text.strip():
            raise HTTPException(
                status_code=400,
                detail="The uploaded document is empty."
            )

        # -----------------------------------------
        # 3. Create chunks
        # -----------------------------------------
        chunks = chunk_text(
            raw_text,
            chunk_size=500,
            overlap=50
        )

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No text chunks could be created."
            )

        logger.info(
            f"Created {len(chunks)} chunks from {filename}"
        )

        # -----------------------------------------
        # 4. Create document ID
        # -----------------------------------------
        doc_id = f"doc_{uuid.uuid4().hex[:8]}"

        # -----------------------------------------
        # 5. Create unique IDs for ChromaDB
        # -----------------------------------------
        ids = [
            f"{doc_id}_chunk_{i}"
            for i in range(len(chunks))
        ]

        # -----------------------------------------
        # 6. Create metadata
        # -----------------------------------------
        metadatas = [
            {
                "doc_id": doc_id,
                "filename": filename,
                "chunk_index": i
            }
            for i in range(len(chunks))
        ]

        # -----------------------------------------
        # 7. Generate embeddings
        # -----------------------------------------
        logger.info(
            f"Generating embeddings for {len(chunks)} chunks..."
        )

        embeddings = rag_engine.embed_batch(chunks)

        if embeddings is None:
            raise Exception(
                "Embedding generation returned None."
            )

        if len(embeddings) != len(chunks):
            raise Exception(
                f"Embedding count ({len(embeddings)}) "
                f"does not match chunk count ({len(chunks)})."
            )

        logger.info(
            "Embeddings generated successfully."
        )

        # -----------------------------------------
        # 8. Store in ChromaDB
        # -----------------------------------------
        logger.info(
            "Adding documents to ChromaDB..."
        )

        db_manager.add_documents(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas
        )

        logger.info(
            "Documents added to ChromaDB successfully."
        )

        # -----------------------------------------
        # 9. Save metadata to SQLite
        # -----------------------------------------
        with SessionLocal() as db:

            doc_log = DocumentLog(
                doc_id=doc_id,
                filename=filename,
                chunk_count=len(chunks),
                created_at=datetime.utcnow()
            )

            db.add(doc_log)
            db.commit()

        # -----------------------------------------
        # 10. Success response
        # -----------------------------------------
        logger.info(
            f"Successfully processed {filename} "
            f"into {len(chunks)} chunks."
        )

        return {
            "message": "File uploaded and indexed successfully.",
            "doc_id": doc_id,
            "filename": filename,
            "chunk_count": len(chunks)
        }

    except HTTPException:
        raise

    except Exception as e:

        logger.exception(
            f"Failed to process document {filename}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/")
async def list_documents():
    """Lists all uploaded documents tracked in the database."""

    try:

        with SessionLocal() as db:

            docs = (
                db.query(DocumentLog)
                .order_by(DocumentLog.created_at.desc())
                .all()
            )

            return [
                {
                    "id": doc.id,
                    "doc_id": doc.doc_id,
                    "filename": doc.filename,
                    "chunk_count": doc.chunk_count,
                    "created_at": (
                        doc.created_at.isoformat()
                        if doc.created_at
                        else None
                    )
                }
                for doc in docs
            ]

    except Exception as e:

        logger.exception(
            "Failed to list documents"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    

    try:

        with SessionLocal() as db:

            doc = (
                db.query(DocumentLog)
                .filter(
                    DocumentLog.doc_id == doc_id
                )
                .first()
            )

            if not doc:
                raise HTTPException(
                    status_code=404,
                    detail="Document not found."
                )

            # Delete vectors from ChromaDB
            db_manager.delete_documents_by_doc_id(
                doc_id
            )

            # Delete metadata from SQLite
            db.delete(doc)
            db.commit()

        return {
            "message": (
                f"Document {doc_id} deleted successfully."
            )
        }

    except HTTPException:
        raise

    except Exception as e:

        logger.exception(
            f"Failed to delete document {doc_id}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )