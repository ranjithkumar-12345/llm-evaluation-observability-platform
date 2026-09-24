import streamlit as st
import requests
import json

# Page Config
st.set_page_config(
    page_title="LLM Evaluation & Observability",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
    <style>
    .metric-card {
        background-color: #1E293B;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #334155;
        text-align: center;
    }
    .metric-val {
        font-size: 2rem;
        font-weight: 700;
        color: #38BDF8;
    }
    .metric-lbl {
        color: #94A3B8;
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar Configuration
st.sidebar.title(" Backend Settings")
backend_url = st.sidebar.text_input(
    "FastAPI Base URL",
    value="http://127.0.0.1:8000",
    help="Use your local URL or live Render deployment URL (e.g., https://your-service.onrender.com)"
).rstrip("/")

# Verify Connectivity
try:
    health_resp = requests.get(f"{backend_url}/", timeout=3)
    if health_resp.status_code == 200:
        st.sidebar.success(" Connected to Backend")
    else:
        st.sidebar.warning(f" Server returned status {health_resp.status_code}")
except Exception:
    st.sidebar.error(" Cannot connect to Backend")

# Header
st.title(" LLM Evaluation & Observability Platform")
st.caption("Automated RAG Triad benchmarking, latency tracking, and telemetry monitoring.")

# ----------------- 1. TELEMETRY & STATS -----------------
st.subheader("System Observability & Global Metrics")

stats_res = None
try:
    resp = requests.get(f"{backend_url}/api/dashboard/stats", timeout=4)
    if resp.status_code == 200:
        stats_res = resp.json()
except Exception:
    pass

c1, c2, c3, c4 = st.columns(4)
with c1:
    total_docs = stats_res.get("total_documents", 0) if stats_res else 0
    st.markdown(f'<div class="metric-card"><div class="metric-val">{total_docs}</div><div class="metric-lbl">Total Documents Indexed</div></div>', unsafe_allow_html=True)
with c2:
    total_evals = stats_res.get("total_evaluations", 0) if stats_res else 0
    st.markdown(f'<div class="metric-card"><div class="metric-val">{total_evals}</div><div class="metric-lbl">Evaluations Tracked</div></div>', unsafe_allow_html=True)
with c3:
    avg_faith = stats_res.get("average_scores", {}).get("faithfulness", 0.0) if stats_res else 0.0
    st.markdown(f'<div class="metric-card"><div class="metric-val">{avg_faith:.2f}</div><div class="metric-lbl">Avg Faithfulness</div></div>', unsafe_allow_html=True)
with c4:
    avg_latency = stats_res.get("average_latency_seconds", 0.0) if stats_res else 0.0
    st.markdown(f'<div class="metric-card"><div class="metric-val">{avg_latency:.2f}s</div><div class="metric-lbl">Avg Latency</div></div>', unsafe_allow_html=True)

st.markdown("---")

# ----------------- 2. TWO TABS: INGESTION & EVALUATION -----------------
tab1, tab2, tab3 = st.tabs([" RAG Query & Evaluation", " Document Ingestion", " Recent Evaluations Log"])

# TAB 1: Evaluation
with tab1:
    col_input, col_eval = st.columns([1, 1])

    with col_input:
        st.write("### Run Evaluation")
        query = st.text_area("User Query", placeholder="e.g., What is Python?", height=100)
        ground_truth = st.text_area("Ground Truth Reference (Optional for ROUGE-L)", placeholder="e.g., Python is a high-level interpreted programming language.", height=80)
        
        run_btn = st.button("Execute & Score RAG", type="primary", use_container_width=True)

    with col_eval:
        st.write("### Evaluation Output")
        if run_btn:
            if not query.strip():
                st.warning("Please enter a query.")
            else:
                payload = {"query": query.strip()}
                if ground_truth.strip():
                    payload["ground_truth"] = ground_truth.strip()

                with st.spinner("Retrieving context, generating response & computing metrics..."):
                    try:
                        res = requests.post(f"{backend_url}/api/evaluate/query", json=payload, timeout=60)
                        if res.status_code == 200:
                            data = res.json()
                            metrics = data.get("metrics", {})

                            st.success("Query Evaluated Successfully!")
                            st.markdown(f"**Generated Answer:**\n\n> {data.get('answer')}")

                            # Metrics Display
                            m1, m2, m3, m4 = st.columns(4)
                            m1.metric("Context Relevance", f"{metrics.get('context_relevance', 0.0):.2f}")
                            m2.metric("Faithfulness", f"{metrics.get('faithfulness', 0.0):.2f}")
                            m3.metric("Answer Relevance", f"{metrics.get('answer_relevance', 0.0):.2f}")
                            m4.metric("Latency", f"{data.get('latency_seconds', 0.0):.2f}s")

                            if metrics.get("rouge_l") is not None:
                                st.metric("ROUGE-L Score", f"{metrics.get('rouge_l'):.2f}")

                            with st.expander("Retrieved Context Chunks"):
                                for idx, ctx in enumerate(data.get("contexts", [])):
                                    st.markdown(f"**Chunk {idx+1}:** {ctx}")
                        else:
                            st.error(f"Error {res.status_code}: {res.text}")
                    except Exception as e:
                        st.error(f"Failed to query backend: {str(e)}")

# TAB 2: Ingestion
with tab2:
    st.write("### Upload & Ingest Knowledge Base Documents")
    st.caption("Supports PDF, DOCX, TXT, CSV, JSON, and MD files with sliding window chunking.")
    
    uploaded_files = st.file_uploader(
        "Choose files", 
        type=["pdf", "docx", "txt", "csv", "json", "md"], 
        accept_multiple_files=True
    )

    if st.button("Upload & Embed Documents", use_container_width=True):
        if not uploaded_files:
            st.warning("Select at least one file.")
        else:
            files_payload = [
                ("files", (f.name, f.read(), f.type or "application/octet-stream"))
                for f in uploaded_files
            ]
            with st.spinner("Processing text extraction, chunking, and embedding..."):
                try:
                    res = requests.post(f"{backend_url}/api/documents/upload", files=files_payload, timeout=120)
                    if res.status_code == 200:
                        doc_data = res.json()
                        st.success(f"Indexed {doc_data.get('uploaded_count')} documents successfully!")
                        st.json(doc_data.get("documents"))
                    else:
                        st.error(f"Upload failed: {res.text}")
                except Exception as e:
                    st.error(f"Error during upload: {str(e)}")

# TAB 3: Telemetry History
with tab3:
    st.write("### Recent Query & Evaluation Telemetry")
    if st.button("Refresh Telemetry Logs"):
        st.rerun()

    try:
        recent_res = requests.get(f"{backend_url}/api/dashboard/recent", timeout=5)
        if recent_res.status_code == 200:
            logs = recent_res.json()
            if logs:
                st.dataframe(logs, use_container_width=True)
            else:
                st.info("No evaluations logged yet.")
    except Exception as e:
        st.error(f"Could not fetch logs: {str(e)}")