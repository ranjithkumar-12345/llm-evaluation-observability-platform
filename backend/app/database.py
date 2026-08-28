import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL","sqlite:///./evals.db")

#create engine and session local
engine = create_engine(DATABASE_URL,connect_args = {"check_same_thread":False})
SessionLocal = sessionmaker(autocommit =False,autoflush=False,bind =engine)


#create base and dependency
base =declarative_base()
def get_db():
    try:
        yield base
    finally:
        base.close()