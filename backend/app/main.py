import uvicorn
import traceback
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .models.schemas import QueryRequest, QueryResponse, UploadResponse
from .services.rag_service import process_pdf_file, query_rag_engine

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": f"{settings.PROJECT_NAME} is running smoothly!"}

@app.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    try:
        num_chunks = process_pdf_file(file)
        return {"message": f"Successfully processed '{file.filename}' into {num_chunks} chunks!"}
    except Exception as e:
        print(f"Upload Error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
async def query_document(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    
    try:
        response = query_rag_engine(request.question)
        return response
    except Exception as e:
        print(f"Query Error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)