"""
FastAPI endpoint for the RAG System
Person 2 — RAG System

Run with:
    uvicorn api:app --host 0.0.0.0 --port 8001 --reload
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rag_pipeline import RAGRetriever, index_all

app = FastAPI(
    title="Smart Clinic RAG API",
    description="Knowledge base retrieval for the Smart Clinic Assistant",
    version="1.0.0",
)

retriever = None

@app.on_event("startup")
def startup():
    global retriever
    try:
        retriever = RAGRetriever()
        print("✅ RAG Retriever loaded.")
    except Exception:
        print("⚠️  Indexing knowledge base first...")
        index_all()
        retriever = RAGRetriever()
        print("✅ RAG Retriever ready.")

class QueryRequest(BaseModel):
    query: str
    n_results: int = 3

class QueryResponse(BaseModel):
    query: str
    context: str
    chunks: list

@app.get("/")
def root():
    return {"message": "Smart Clinic RAG API is running 🏥"}

@app.get("/health")
def health():
    return {"status": "ok", "retriever_ready": retriever is not None}

@app.post("/retrieve")
def retrieve(req: QueryRequest):
    if retriever is None:
        raise HTTPException(status_code=503, detail="Retriever not ready.")
    chunks = retriever.retrieve(req.query, req.n_results)
    context = retriever.retrieve_formatted(req.query, req.n_results)
    return {"query": req.query, "context": context, "chunks": chunks}

@app.post("/reindex")
def reindex():
    global retriever
    try:
        index_all()
        retriever = RAGRetriever()
        return {"message": "Re-indexed successfully ✅"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/patient/{patient_id}")
def get_patient_history(patient_id: str):
    if retriever is None:
        raise HTTPException(status_code=503, detail="Retriever not ready.")
    chunks = retriever.retrieve(f"patient history for patient ID {patient_id}", n_results=10)
    patient_chunks = [c for c in chunks if c["metadata"].get("patient_id") == patient_id]
    if not patient_chunks:
        raise HTTPException(status_code=404, detail=f"No records found for: {patient_id}")
    return {
        "patient_id": patient_id,
        "records": patient_chunks,
        "context": "\n\n---\n\n".join(c["text"] for c in patient_chunks),
    }