from datetime import datetime
from sqlalchemy import Column,String,Integer,Float,Text,DateTime
from app.databasee import Base,engine

class EvaluationLog(Base):
    __tablename__ = "evaluation_logs"
    id =Column(Integer ,primary_key =True,index = True)
    query = Column(Text,nullable=False)
    retrieved_context=Column(Text, nullable=True)
    generated_answer = Column(Text, nullable=False)
    context_relevance = Column(Float, nullable=True)
    faithfulness = Column(Float, nullable=True)
    answer_relevance = Column(Float, nullable=True)
    reasoning = Column(Text, nullable=True)
    latency_seconds = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


class DocumentLog(Base):
    __tablename__ = "document_logs"

    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String, unique=True, index=True, nullable=False)
    filename = Column(String, nullable=False)
    chunk_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


if __name__ =="__main__":
    Base.metadata.create_all(bind=engine)
    print("Tables Created Successfully")