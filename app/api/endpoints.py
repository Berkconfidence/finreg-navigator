from fastapi import APIRouter, HTTPException
from app.models.schemas import QueryRequest, QueryResponse
from app.services.rag_service import rag_service
import mlflow
import time

router = APIRouter()

@router.post("/ask", response_model=QueryResponse)
async def ask_compliance_question(request: QueryRequest):
    """
    Bankacılık mevzuatı ile ilgili soruları RAG motoruna iletir.
    """
    try:
        start_time = time.time()
        
        result = rag_service.ask_question(request.question)
        
        latency = time.time() - start_time
        
        with mlflow.start_run(run_name="Live_Query", nested=True):
            mlflow.log_param("question", request.question)
            mlflow.log_metric("latency_sec", latency)
            
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG Motoru hatası: {str(e)}")