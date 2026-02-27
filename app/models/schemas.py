from pydantic import BaseModel, Field
from typing import List, Optional

class QueryRequest(BaseModel):
    """Kullanıcıdan gelen soru isteği şeması"""
    question: str = Field(..., example="Açık bankacılık servisleri nedir?")

class SourceNodeMetadata(BaseModel):
    """Cevabın kaynağına dair bilgiler"""
    file_name: str
    page_label: str
    article_no: Optional[str] = "Belirtilmemiş"

class QueryResponse(BaseModel):
    """Kullanıcıya dönecek cevap şeması"""
    answer: str
    sources: List[SourceNodeMetadata]