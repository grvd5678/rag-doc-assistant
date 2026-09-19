# 🤖 DocuMind AI - Full-Stack RAG Document Assistant

DocuMind AI is an intelligent Retrieval-Augmented Generation (RAG) platform that allows users to upload PDF documents and ask questions in natural language. Powered by FastAPI, React, LangChain, and Google Gemini, it synthesizes long documents into structured summaries with precise page-level citations.

---

## ✨ Features

- **📄 Smart PDF Ingestion**: Parses PDF documents into contextual chunks with metadata tracking.
- **💬 Conversational Q&A**: Context-aware LLM answers powered by `Google Gemini`.
- **📌 Precise Citations**: Displays exact source files, page numbers, and preview snippets for total transparency.
- **⚡ Fast & Responsive**: Built with FastAPI backend and Vite + React + Tailwind CSS UI.
- **🏗️ Modular Architecture**: Fully decoupled backend split into `core`, `models`, and `services`.

---

## 🏗️ Project Architecture

```text
rag-doc-assistant/
├── backend/
│   ├── app/
│   │   ├── core/         # Settings & env configurations
│   │   ├── models/       # Pydantic schemas (Request/Response)
│   │   ├── services/     # RAG pipeline & LLM chain logic
│   │   └── main.py       # FastAPI routing & CORS middleware
│   ├── requirements.txt  # Python dependencies
│   └── .env              # Environment variables
└── frontend/
    ├── src/
    │   ├── components/   # FileUpload, ChatBox, Sources
    │   └── App.jsx
    └── package.json

🚀 Quick Start Guide
1. Backend Setup
Bash
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
Create a .env file inside backend/:

Code snippet
GEMINI_API_KEY=your_gemini_api_key_here
Run the FastAPI server:

Bash
python -m uvicorn app.main:app --reload
2. Frontend Setup
Bash
cd frontend
npm install
npm run dev
Open http://localhost:5173 in your browser!


5. Press **`Ctrl + S`** to save!

That wraps up the documentation for your project! You've officially got a complete, modular, full-stack RAG app ready to present anywhere!