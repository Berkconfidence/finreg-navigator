from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.endpoints import router as api_router
from app.core.config import settings
import mlflow
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: MLflow bağlantısı uygulama ayağa kalktıktan sonra kurulur
    mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000"))
    mlflow.set_experiment("FinReg_Live_API")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Bankacılık Mevzuat ve Uyum Analitik Platformu",
    lifespan=lifespan
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "qdrant_connected", "llm": "ollama_ready"}