from datetime import datetime
from sqlalchemy import Column,String,Integer,Float,Text,DateTime
from app.database import base

class EvaluationLog(base):
    __tablename__ = "Evaluation_logs"
    id,
