from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "FinReg Navigator"
    VERSION: str = "1.0.0"
    
    QDRANT_URL: str = "http://localhost:6333"
    COLLECTION_NAME: str = "bank_compliance_v1"
    
    EMBED_MODEL_NAME: str = "intfloat/multilingual-e5-base"
    LLM_MODEL_NAME: str = "llama3"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    SIMILARITY_TOP_K: int = 5
    
    class Config:
        env_file = ".env"

settings = Settings()