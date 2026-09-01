import io
import uuid
from typing import List
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException
import PyPDF2

from app.databasee import SessionLocal
from app.database.db_manager import db_manager
from app.models import DocumentLog
from app.rag.engine import rag_engine
from app.logging_config import logger

router = APIRouter()


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    
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
    
    filename = file.filename
    content = await file.read()
    raw_text = ""

    try:
        if filename.endswith(".pdf"):
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    raw_text += extracted + "\n"
        elif filename.endswith(".txt"):
            raw_text = content.decode("utf-8")
        else:
            raise HTTPException(status_code=400, detail="Only .pdf and .txt files are supported.")

        if not raw_text.strip():
            raise HTTPException(status_code=400, detail="The uploaded document is empty.")

        chunks = chunk_text(raw_text)
        doc_id = f"doc_{uuid.uuid4().hex[:8]}"

        
        documents_payload = []
        for i, chunk in enumerate(chunks):
            documents_payload.append({
                "id": f"{doc_id}_chunk_{i}",
                "content": chunk,
                "metadata": {"doc_id": doc_id, "filename": filename, "chunk_index": i}
            })

        
        embeddings = rag_engine.embed_batch(chunks)
        db_manager.add_documents(documents=documents_payload, embeddings=embeddings)

        
        with SessionLocal() as db:
            doc_log = DocumentLog(
                doc_id=doc_id,
                filename=filename,
                chunk_count=len(chunks),
                created_at=datetime.utcnow()
            )
            db.add(doc_log)
            db.commit()

        logger.info(f"Successfully processed {filename} into {len(chunks)} chunks.")
        return {
            "message": "File uploaded and indexed successfully.",
            "doc_id": doc_id,
            "filename": filename,
            "chunk_count": len(chunks)
        }
    except Exception as e:
        logger.error(f"Failed to process document {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_documents():
    """Lists all uploaded documents tracked in the database."""
    with SessionLocal() as db:
        docs = db.query(DocumentLog).order_by(DocumentLog.created_at.desc()).all()
        return [
            {
                "id": doc.id,
                "doc_id": doc.doc_id,
                "filename": doc.filename,
                "chunk_count": doc.chunk_count,
                "created_at": doc.created_at.isoformat() if doc.created_at else None
            }
            for doc in docs
        ]


@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    
    with SessionLocal() as db:
        doc = db.query(DocumentLog).filter(DocumentLog.doc_id == doc_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found.")

        
        db.delete(doc)
        db.commit()

    return {"message": f"Document {doc_id} deleted successfully."}