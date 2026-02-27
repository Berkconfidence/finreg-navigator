from fastapi import FastAPI
from app.api.endpoints import router as api_router
from app.core.config import settings
import mlflow

mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("FinReg_Live_API")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Bankacılık Mevzuat ve Uyum Analitik Platformu"
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "qdrant_connected", "llm": "ollama_ready"}