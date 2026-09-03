# 📊 **LLM Evaluation & Observability Platform**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![Google Gemini](https://img.shields.io/badge/Gemini-3.6--Flash-orange.svg)](https://ai.google.dev)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-yellow.svg)](https://chromadb.dev)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Render](https://img.shields.io/badge/Render-Deployed-blueviolet.svg)](https://render.com)

A production-ready evaluation and observability platform for Retrieval-Augmented Generation (RAG) pipelines built with FastAPI, Google Gemini Flash, ChromaDB, and SQLite. Features automated tri-metric evaluation (Context Relevance, Faithfulness, Answer Relevance), ROUGE-L ground truth benchmarking, multi-format document ingestion, and historical telemetry tracking.

---

## 🚀 **Key Features**

| Feature | Description |
|---------|-------------|
| **Multi-Format Ingestion** | Text parsing and sliding window chunking across `.pdf`, `.docx`, `.txt`, `.csv`, `.json`, and `.md` formats |
| **RAG Triad Evaluation** | Real-time scoring for Context Relevance, Faithfulness (hallucination detection), and Answer Relevance |
| **Ground Truth Benchmarking** | ROUGE-L syntactic and semantic overlap scoring against golden reference datasets |
| **Persistent Vector Storage** | ChromaDB integration backed by Google's lightweight `text-embedding-004` API for ultra-low memory usage |
| **Observability & Telemetry** | SQLite-backed query logging, metric tracking, and latency profiling with historical stats endpoints |
| **Batch Processing** | Evaluate multiple queries at once with aggregated metrics and statistical summaries |

---

## 🏗️ **Architecture Flow**

```
┌─────────────────────────────────────────────────────────────┐
│                           CLIENT                            │
│                    (Browser / API Client)                   │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       FastAPI Backend                       │
│  ┌────────────────────┐ ┌──────────────────┐ ┌────────────┐ │
│  │/api/documents/upload│ │/api/evaluate/query│ │ /dashboard │ │
│  └─────────┬──────────┘ └────────┬─────────┘ └─────┬──────┘ │
└────────────┼─────────────────────┼─────────────────┼────────┘
             │                     │                 │
             ▼                     ▼                 ▼
┌──────────────────────┐  ┌──────────────────┐ ┌─────────────┐
│ Multi-Format Parser  │  │ RAG Query Engine │ │ SQLite Logs │
│ (PDF/DOCX/TXT/CSV/MD)│  │ (Retrieval + LLM)│ │ (Telemetry) │
└────────────┬─────────┘  └────────┬─────────┘ └─────────────┘
             │                     │        ▲
             ▼                     ▼        │
┌─────────────────┐   ┌────────────────┐    │
│ Sliding Window  │   │ Google Gemini  │    │
│  Text Chunks    │   │  (3.6-Flash)   │    │
└────────┬────────┘   └────────────────┘    │
         │                           │       │
         ▼                           ▼       │
┌─────────────────┐           ┌──────────────────┐
│ ChromaDB Vector │──────────►│Evaluation Engine │
│      Store      │           │RAG Triad+ROUGE-L │
└─────────────────┘           └──────────────────┘
```

---

## 📁 **Project Structure**

```
llm-evaluation-observability-platform/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py                 # Pydantic environment settings
│   │   ├── logging_config.py         # Centralized logging setup
│   │   ├── main.py                   # FastAPI application entrypoint
│   │   ├── models.py                 # SQLAlchemy ORM schemas
|   |   |── databasee.py              # Created BASE AND Engine
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   └── db_manager.py         # ChromaDB & SQLite connections
│   │   ├── evaluation/
│   │   │   ├── __init__.py
│   │   │   ├── evaluator.py          # Tri-metric evaluation pipeline
│   │   │   └── metrics.py            # Similarity & ROUGE scorers
│   │   ├── rag/
│   │   │   ├── __init__.py
│   │   │   └── engine.py             # Gemini client & retrieval
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── dashboard.py          # Metrics & stats endpoints
│   │       ├── documents.py          # Multi-format upload endpoints
│   │       └── evaluation.py         # Single & batch query endpoints
│   ├── chroma_db/                    # Vector database storage
│   ├── logs/                         # Application logs
│   ├── uploads/                      # Temporary file storage
│   ├── .env                          # Environment variables (not in git)
│   ├── .env.example                  # Example environment variables
│   ├── .gitignore
│   └── requirements.txt
├── frontend/                         # Frontend dashboard (optional)
├── tests/                            # Unit & integration tests
├── .dockerignore                     # Ignore the Environment Variables
├── render.yml                        # Cloud deployment blueprint
└── README.md                         # This file
```

---

## ⚙️ **Setup & Installation**

### 1. Clone the Repository

```bash
git clone https://github.com/ranjithkumar-12345/llm-evaluation-observability-platform.git
cd llm evaluation & observability platform
```

### 2. Create Virtual Environment

```bash
# Windows:
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux/macOS:
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Required
GEMINI_API_KEY=your_actual_gemini_api_key_here

# Optional (with defaults)
TOP_K_RETRIEVAL=5
CHROMA_PERSIST_DIR=./chroma_db
APP_HOST=127.0.0.1
APP_PORT=8000
LOG_LEVEL=INFO
```

### 5. Run the Application

```bash
# From backend directory
uvicorn app.main:app --reload
```

Server will start at: `http://127.0.0.1:8000`

### 6. Access API Documentation

- **Swagger UI:** `http://127.0.0.1:8000/docs`
- **ReDoc:** `http://127.0.0.1:8000/redoc`

---

## 🔌 **API Endpoints**

| Method | Endpoint | Description | Payload Type |
|--------|----------|-------------|--------------|
| **POST** | `/api/documents/upload` | Upload multiple files (`.pdf`, `.docx`,'.txt' ) | `multipart/form-data` |
| **GET** | `/api/documents/` | List all indexed documents and chunk statistics | None |
| **DELETE** | `/api/documents/{doc_id}` | Remove document entry from tracking database | None |
| **POST** | `/api/evaluate/query` | Run single query with RAG triad evaluation | `application/json` |
| **POST** | `/api/evaluate/batch` | Execute automated batch benchmark run | `application/json` |
| **GET** | `/api/evaluate/metrics` | Get list of available evaluation metrics | None |
| **GET** | `/api/dashboard/stats` | Global metrics, average scores, and latency stats | None |
| **GET** | `/api/dashboard/recent` | Retrieve latest query evaluation logs | None |
| **GET** | `/api/dashboard/metrics-chart` | Get data for metrics visualization charts | None |
| **GET** | `/api/dashboard/performance` | Get performance data over time | None |

---

## 🧪 **Example Usage**

### 1. Upload Documents

```http
POST /api/documents/upload
Content-Type: multipart/form-data

files: [document1.pdf, data.csv, readme.md]
```

**Response:**
```json
{
  "success": true,
  "uploaded": 3,
  "failed": 0,
  "total_files": 3,
  "documents": [
    {
      "id": "abc-123",
      "filename": "document1.pdf",
      "size_kb": 245.6,
      "type": "PDF Document"
    },
    {
      "id": "def-456",
      "filename": "data.csv",
      "size_kb": 12.3,
      "type": "CSV File"
    }
  ]
}
```

### 2. Evaluate Query

**Request:**
```http
POST /api/evaluate/query
Content-Type: application/json

{
  "query": "What is Python?",
  "ground_truth": "Python is a high-level, interpreted, general-purpose programming language widely used in AI and data science."
}
```

**Response:**
```json
{
  "query": "What is Python?",
  "answer": "Python is a high-level, interpreted, general-purpose programming language known for its simple syntax and strong AI ecosystem.",
  "contexts": [
    "Python is a programming language that lets you work quickly and integrate systems more effectively.",
    "Python is widely used in data science, machine learning, and AI applications."
  ],
  "metrics": {
    "context_relevance": 0.94,
    "faithfulness": 1.0,
    "answer_relevance": 0.96,
    "rouge_l": 0.88,
    "completeness": 0.92
  },
  "latency_seconds": 1.12
}
```

### 3. Batch Evaluation

**Request:**
```http
POST /api/evaluate/batch
Content-Type: application/json

{
  "queries": [
    "What is machine learning?",
    "How does neural network work?",
    "Explain supervised learning"
  ]
}
```

**Response:**
```json
{
  "total": 3,
  "results": [
    {
      "query": "What is machine learning?",
      "answer": "Machine learning is a subset of AI...",
      "metrics": { "context_relevance": 0.91, "answer_relevance": 0.89 }
    },
    {
      "query": "How does neural network work?",
      "answer": "A neural network works by...",
      "metrics": { "context_relevance": 0.85, "answer_relevance": 0.92 }
    }
  ]
}
```

---

## 🖥️ **Testing with Swagger UI**

1. Open `http://127.0.0.1:8000/docs` in your browser

2. **Upload Documents:**
   - Expand `POST /api/documents/upload`
   - Click **Try it out**
   - Click **Choose Files** and select your documents
   - Click **Execute** to chunk, vectorize, and store them in ChromaDB

3. **Evaluate Query:**
   - Expand `POST /api/evaluate/query`
   - Click **Try it out**
   - Supply a test `query` and optional `ground_truth`
   - Click **Execute** to run the RAG pipeline

4. **Check Dashboard:**
   - Expand `GET /api/dashboard/stats`
   - Click **Try it out** then **Execute**
   - Review real-time system performance metrics

5. **List Documents:**
   - Expand `GET /api/documents/`
   - Click **Execute**
   - View all uploaded documents and their chunks

---

## 🚀 **Deployment on Render**

### Quick Deploy Steps:

1. Push your code to GitHub
2. Create a `render.yml` file in the root directory
3. Connect your GitHub repository to Render
4. Render will automatically detect the configuration and deploy

### Environment Variables Required:

| Variable | Description | Example |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | `AIzaSy...` |
| `TOP_K_RETRIEVAL` | Number of chunks to retrieve | `5` |
| `CHROMA_PERSIST_DIR` | ChromaDB storage path | `./chroma_db` |

### Live Demo URL:
```
https://llm-evaluation-observability-platform.onrender.com/docs
```

---

## 🔧 **Troubleshooting**

### Common Issues:

| Issue | Solution |
|-------|----------|
| **ModuleNotFoundError** | Run `pip install -r requirements.txt` |
| **ChromaDB connection error** | Ensure `chroma_db/` directory exists and is writable |
| **Gemini API key error** | Check `.env` file has valid `GEMINI_API_KEY` |
| **No documents found** | Upload documents via `/api/documents/upload` |
| **Slow embeddings** | Use `embed_batch()` for multiple texts |
| **PermissionError on Windows** | Run VS Code/PowerShell as Administrator |

---

## 📊 **Evaluation Metrics Explained**

| Metric | Description | Score Range |
|--------|-------------|-------------|
| **Context Relevance** | How relevant are the retrieved documents to the query? | 0.0 - 1.0 |
| **Faithfulness** | Is the answer grounded in the retrieved context? | 0.0 - 1.0 |
| **Answer Relevance** | Does the answer directly address the query? | 0.0 - 1.0 |
| **Completeness** | Is the answer complete compared to ground truth? | 0.0 - 1.0 |
| **ROUGE-L** | Text overlap with ground truth (semantic similarity) | 0.0 - 1.0 |

---

## 📜 **License**

Distributed under the MIT License. See `LICENSE` for more information.

---

## 👤 **Author**

**Your Name**
- GitHub: [@ranjithkumar-12345](https://github.com/ranjithkumar-12345)
- Email: ranjithkumar180205@gmail.com

---

## 🙏 **Acknowledgments**

- **Google Gemini** for providing the AI models
- **FastAPI** for the web framework
- **ChromaDB** for vector storage
- **Sentence Transformers** for embedding generation

---

## 🔗 **Links**

- **Interactive API Docs (Swagger UI):** [(https://llm-evaluation-observability-platform.onrender.com)/docs] (https://llm-evaluation-observability-platform.onrender.com/docs)
- **Alternative API Docs (ReDoc):** [https://llm-evaluation-observability-platform.onrender.com/docs]( https://llm-evaluation-observability-platform.onrender.com/redoc)
- **GitHub Repository:** [https://github.com/YOUR_USERNAME/llm-evaluation-observability-platform](https://github.com/ranjithkumar-12345/llm-evaluation-observability-platform)

---

> Built with ❤️ using FastAPI, Google Gemini, ChromaDB, and SQLite

