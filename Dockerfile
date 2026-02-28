FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir llama-index-embeddings-huggingface

RUN python -c "\
from fastembed import SparseTextEmbedding; \
SparseTextEmbedding('prithivida/Splade_PP_en_v1'); \
print('Sparse model downloaded successfully')"

RUN python -c "\
from llama_index.embeddings.huggingface import HuggingFaceEmbedding; \
HuggingFaceEmbedding(model_name='intfloat/multilingual-e5-base'); \
print('Dense embedding model downloaded successfully')"

COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]