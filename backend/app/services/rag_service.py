import os
from fastapi import UploadFile, HTTPException
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from ..core.config import settings

from app.core.config import settings

chunks_storage = []

def process_pdf_file(file: UploadFile) -> int:
    global chunks_storage
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    
    file.file.seek(0)
    content = file.file.read()
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    reader = PdfReader(file_path)
    documents = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            documents.append(Document(page_content=text, metadata={"page": i + 1, "source": file.filename}))
    
    if not documents:
        raise HTTPException(status_code=400, detail="No readable text found in PDF.")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks_storage = text_splitter.split_documents(documents)
    
    return len(chunks_storage)

def query_rag_engine(query: str):
    global chunks_storage
    if not chunks_storage:
        return {"answer": "Please upload a document first before asking questions!", "sources": []}
    
    query_words = set(query.lower().split())
    sorted_chunks = sorted(
        chunks_storage, 
        key=lambda doc: len(query_words.intersection(set(doc.page_content.lower().split()))), 
        reverse=True
    )
    top_docs = sorted_chunks[:3]
    context = "\n\n".join([f"--- Page {doc.metadata.get('page', 1)} ---\n" + doc.page_content for doc in top_docs])

    sources = [
        {
            "page": doc.metadata.get("page", 1),
            "source": doc.metadata.get("source", "Unknown"),
            "snippet": doc.page_content[:150] + "..."
        }
        for doc in top_docs
    ]

    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return {
            "answer": "GEMINI_API_KEY is missing in backend/.env file. Please add your key to proceed.",
            "sources": sources
        }

    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-3.6-flash",
            temperature=0.2,
            google_api_key=api_key
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are DocuMind AI, an intelligent document assistant. "
                       "Answer the user's question concisely, clearly, and naturally based ONLY on the provided context below. "
                       "If the information is not present in the context, politely state that you cannot find it in the uploaded document.\n\n"
                       "Context from PDF:\n{context}"),
            ("human", "{question}")
        ])
        
        chain = prompt | llm | StrOutputParser()
        response_text = chain.invoke({"context": context, "question": query})
        
        return {
            "answer": response_text,
            "sources": sources
        }
    except Exception as e:
        return {
            "answer": f"API Error: {str(e)}. (Fallback excerpt context):\n\n{context}",
            "sources": sources
        }