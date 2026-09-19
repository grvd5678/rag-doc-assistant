import os
from fastapi import UploadFile, HTTPException
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from ..core.config import settings

CHROMA_PERSIST_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "chroma_db")
)
os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
COLLECTION_NAME = "documind_docs"

def get_embeddings():
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured.")
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=api_key
    )

def get_vector_store():
    embeddings = get_embeddings()
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_PERSIST_DIR
    )

def process_pdf_file(file: UploadFile) -> int:
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
            documents.append(
                Document(
                    page_content=text,
                    metadata={"page": i + 1, "source": file.filename}
                )
            )
    
    if not documents:
        raise HTTPException(status_code=400, detail="No readable text found in PDF.")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    
    # Store into Chroma vector store with persistent storage
    vector_store = get_vector_store()
    vector_store.add_documents(chunks)
    
    return len(chunks)

def query_rag_engine(query: str):
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return {
            "answer": "GEMINI_API_KEY is missing in backend/.env file. Please add your key to proceed.",
            "sources": []
        }

    try:
        vector_store = get_vector_store()
        doc_count = vector_store._collection.count()
        if doc_count == 0:
            return {
                "answer": "Please upload a document first before asking questions!",
                "sources": []
            }
        
        # Retrieve top 4 most relevant chunks via Chroma semantic vector search
        top_docs = vector_store.similarity_search(query, k=4)
        if not top_docs:
            return {
                "answer": "No relevant content found in the uploaded documents for your query.",
                "sources": []
            }
            
        context = "\n\n".join([
            f"--- Source: {doc.metadata.get('source', 'Document')} | Page {doc.metadata.get('page', 1)} ---\n" + doc.page_content
            for doc in top_docs
        ])

        sources = [
            {
                "page": int(doc.metadata.get("page", 1)),
                "source": str(doc.metadata.get("source", "Unknown")),
                "snippet": doc.page_content[:150] + "..."
            }
            for doc in top_docs
        ]

        llm = ChatGoogleGenerativeAI(
            model="gemini-3.6-flash",
            google_api_key=api_key
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are DocuMind AI, an intelligent and helpful document assistant. "
                       "Answer the user's question concisely, clearly, and accurately based ONLY on the provided context below. "
                       "Use formatted markdown with bolding, lists, or code blocks where appropriate for clarity. "
                       "If the information is not present in the context, politely state that you cannot find it in the uploaded document.\n\n"
                       "Context from PDF documents:\n{context}"),
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
            "answer": f"Error querying document: {str(e)}",
            "sources": []
        }