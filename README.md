# 🤖 DocuMind AI — Production-Grade RAG Document Assistant

[![React](https://img.shields.io/badge/Frontend-React_19_+_Vite-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/Orchestration-LangChain-1C3C3C?logo=langchain&logoColor=white)](https://www.langchain.com/)
[![ChromaDB](https://img.shields.io/badge/Vector_DB-ChromaDB-FF6600)](https://www.trychroma.com/)
[![Gemini](https://img.shields.io/badge/AI_Model-Google_Gemini_3.6_Flash-4285F4?logo=google&logoColor=white)](https://ai.google.dev/)
[![Vercel](https://img.shields.io/badge/Deployment-Vercel-000000?logo=vercel&logoColor=white)](https://vercel.com/)

**DocuMind AI** is an advanced, production-grade Retrieval-Augmented Generation (RAG) platform designed to tackle the real-world limitations of naive vector search. Powered by **FastAPI**, **React 19**, **ChromaDB**, and **Google Gemini**, it features **Hybrid Retrieval (BM25 + Dense Vectors with Reciprocal Rank Fusion)**, an **Automated Faithfulness & Hallucination Guardrail**, and **Sub-50ms Semantic Response Caching** with verifiable page citations.

---

## 🌐 Live Production Demo

* **Live Frontend**: [https://rag-doc-assistant-pearl.vercel.app/](https://rag-doc-assistant-pearl.vercel.app/)
* **Backend Cloud Infrastructure**: AWS EC2 (Ubuntu t3.micro), Uvicorn ASGI server, Nginx reverse proxy.

---

## 🚀 Key Engineering Upgrades

### 1. 🎯 Hybrid Retrieval & Reciprocal Rank Fusion (RRF)
* **The Problem**: Pure semantic vector search (cosine similarity) often misses exact keyword queries (acronyms, code identifiers, dates, product IDs), while lexical search misses conceptual context.
* **The Solution**: Combines dense vector retrieval (ChromaDB + Gemini 3072-dim embeddings) with sparse keyword retrieval (`BM25Okapi`). Rankings are fused using **Reciprocal Rank Fusion**:
  $$RRF\_Score(d) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$
  Ensures both conceptual matches and exact token matches surface in the top-k context.

### 2. 🛡️ Automated Faithfulness & Hallucination Guardrail
* **The Problem**: LLMs can introduce hallucinations or ungrounded assertions when synthesizing complex PDF context.
* **The Solution**: An automated evaluation step audits every generated response against retrieved chunks before finalizing the response. Computes:
  * **Faithfulness Score (0.0 - 1.0)**: Entailment percentage of claims strictly supported by document context.
  * **Groundedness Verdict**: `FAITHFUL`, `PARTIALLY_GROUNDED`, or `UNGROUNDED`.
  * Visual verification badge displayed directly in the UI.

### 3. ⚡ Sub-50ms Semantic Response Caching
* **The Problem**: Repetitive queries incur repeated LLM latency (2–4s) and unnecessary API token costs.
* **The Solution**: Persistent response cache with query normalization. Repeated or identical queries return verified answers, citations, and evaluation metadata in **<50ms** with zero LLM token consumption.

---

## 🏗️ System Architecture

```text
User Question
    │
    ▼
[ 1. Semantic & Exact Cache ] ──(Cache Hit: <50ms)──► Instant Response
    │ (Cache Miss)
    ▼
[ 2. Hybrid Retrieval Engine ]
    ├── Dense Vector Search (ChromaDB + Gemini Embeddings 3072-dim)
    └── Sparse Lexical Search (BM25Okapi)
    │
    ▼
[ Reciprocal Rank Fusion (RRF) ] ──► Top-4 Fused Chunks
    │
    ▼
[ Gemini 3.6 Flash Synthesis ] ──► Grounded Answer + Citations
    │
    ▼
[ 3. Faithfulness & Hallucination Guardrail ] ──► Computes Grounding Score %
    │
    ▼
Update Cache ──► Client Interface (React 19 + Diagnostics Badge)
```

---

## 🛠️ Tech Stack

| Component | Technologies |
| :--- | :--- |
| **Frontend** | React 19, Vite, Tailwind CSS v4, Lucide React, Axios, React-Markdown |
| **Backend** | Python 3, FastAPI, Uvicorn, Pydantic v2, python-dotenv |
| **Retrieval & RAG** | LangChain Core, ChromaDB, `rank-bm25`, Reciprocal Rank Fusion, PyPDF |
| **AI Models** | `gemini-3.6-flash`, `models/gemini-embedding-001` (3072 dimensions) |
| **Evaluation & Cache** | Automated Faithfulness Guardrail, SQLite Persistence Cache |
| **Cloud & DevOps** | AWS EC2 (Ubuntu), Nginx, Vercel Edge Network |

---

## 💻 Local Quickstart

### 1. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate   # Windows
# source venv/bin/activate # Linux / macOS

# Install dependencies
pip install -r requirements.txt

# Create .env file with your Google Gemini API Key
echo "GEMINI_API_KEY=your_gemini_api_key_here" > .env

# Run FastAPI server
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend

# Install packages
npm install

# Run Vite dev server
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser!
