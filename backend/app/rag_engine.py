import os
import uuid
import chromadb
from dotenv import load_dotenv
from datetime import datetime
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL","gemmni-flash-latest")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR","./chroma_db")

class RAGEngine():

    def __init__(self):

   