# 🤖 DocuMind AI — Full-Stack RAG Document Assistant

[![React](https://img.shields.io/badge/Frontend-React_19_+_Vite-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/Orchestration-LangChain-1C3C3C?logo=langchain&logoColor=white)](https://www.langchain.com/)
[![ChromaDB](https://img.shields.io/badge/Vector_DB-ChromaDB-FF6600)](https://www.trychroma.com/)
[![Gemini](https://img.shields.io/badge/AI_Model-Google_Gemini_3.6_Flash-4285F4?logo=google&logoColor=white)](https://ai.google.dev/)
[![Vercel](https://img.shields.io/badge/Deployment-Vercel-000000?logo=vercel&logoColor=white)](https://vercel.com/)

**DocuMind AI** is a production-ready, full-stack Retrieval-Augmented Generation (RAG) platform. Users can upload complex PDF documents and ask natural-language questions to receive contextually grounded answers synthesized by **Google Gemini**, backed by true semantic vector search via **ChromaDB** with exact page-level citations.

---

## 🌐 Live Demo & Deployment

* **Frontend (Vercel)**: Connect your repository to Vercel (Root Directory: `frontend`) for automated CI/CD.
* **Backend (AWS EC2)**: Deployed on an AWS Ubuntu instance running Uvicorn and Nginx reverse proxy.

---

## ✨ Key Features

- **📄 Robust PDF Parsing**: Ingests multi-page PDFs using `pypdf` with per-page metadata tracking.
- **🧠 True Semantic Vector Search**: Embeds document chunks using `GoogleGenerativeAIEmbeddings` (`models/gemini-embedding-001`) and indexes them into persistent **ChromaDB** vector storage.
- **💬 Conversational Q&A with Gemini**: Context-aware synthesis powered by `gemini-3.6-flash` via LangChain LCEL chains.
- **📌 Transparent Page-Level Citations**: Shows the exact source filename, page number, and text snippet preview for complete auditability.
- **🎨 Modern Dark UI with Markdown**: React 19 + Tailwind CSS interface rendering formatted markdown, bullet points, and code blocks using `react-markdown`.
- **⚡ Decoupled & Cloud-Ready**: FastAPI backend with CORS middleware and Vite proxy for seamless local development and production Vercel/EC2 deployments.

---

## 🏗️ Architecture

```text
rag-doc-assistant/
├── backend/
│   ├── app/
│   │   ├── core/               # Configuration & env management
│   │   ├── models/             # Pydantic schemas (QueryRequest, QueryResponse)
│   │   ├── services/           # RAG pipeline, ChromaDB indexing & Gemini LLM
│   │   └── main.py             # FastAPI routing & CORS middleware
│   ├── chroma_db/              # Persistent Chroma vector database
│   ├── uploaded_files/         # PDF upload directory
│   ├── requirements.txt        # Python backend dependencies
│   └── .env                    # Secrets & GEMINI_API_KEY
└── frontend/
    ├── src/
    │   ├── components/         # FileUpload, ChatBox (Markdown), Sources
    │   ├── App.jsx             # Main dashboard layout
    │   └── index.css           # Tailwind CSS styling
    ├── package.json            # React 19, Vite, Tailwind, Lucide, ReactMarkdown
    ├── vercel.json             # Vercel SPA routing & backend proxy rewrites
    └── vite.config.js          # Vite config with local dev proxy
```

---

## 🛠️ Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 19, Vite 8, Tailwind CSS v4, Lucide React, Axios, React-Markdown |
| **Backend** | Python 3, FastAPI, Uvicorn, Pydantic v2, python-dotenv |
| **RAG & AI** | LangChain Core, `langchain-google-genai`, ChromaDB, PyPDF |
| **Cloud & DevOps** | AWS EC2 (Ubuntu), Nginx Reverse Proxy, Vercel CI/CD |

---

## 🚀 Quick Start Guide

### 1. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure your Gemini API key in backend/.env
echo "GEMINI_API_KEY=your_gemini_api_key_here" > .env

# Run FastAPI server with auto-reload
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start Vite development server (proxies /upload and /query to port 8000)
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser!

---

## ☁️ Deploying to Vercel

1. Push this repository to GitHub.
2. Go to [Vercel Dashboard](https://vercel.com/dashboard) → **Add New...** → **Project**.
3. Import your `rag-doc-assistant` repository.
4. Set **Root Directory** to `frontend`.
5. Click **Deploy**!