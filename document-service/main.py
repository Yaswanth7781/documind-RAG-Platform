from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from document_service import process_pdf
from shared.services.vector_store import get_all_documents, delete_document
from shared.core.security import verify_token

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="UniGuard AI - Document Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post(
    "/documents/upload",
    summary="Upload Enterprise Document",
    description="Uploads static PDF file, parses its text, and vectors it to ChromaDB/Pinecone.",
    dependencies=[Depends(verify_token)]
)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400, 
            detail="Only PDF files are supported for Enterprise Document ingestion."
        )
        
    try:
        result_message = await process_pdf(file)
        return {"status": "success", "message": result_message}
    except Exception as e:
        raise HTTPException(500, detail=f"Failed to process document: {e}")

@app.get(
    "/documents/list",
    summary="List all uploaded documents"
)
def list_documents():
    docs = get_all_documents()
    return {"status": "success", "documents": docs}

@app.delete(
    "/documents/{filename}",
    summary="Delete an enterprise document",
    dependencies=[Depends(verify_token)]
)
def remove_document(filename: str):
    try:
        delete_document(filename)
        return {"status": "success", "message": f"Deleted {filename} from vector store."}
    except Exception as e:
        raise HTTPException(500, detail=f"Failed to delete document: {e}")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "document-service"}
