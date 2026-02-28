# FinReg Navigator

Bankacılık mevzuatı üzerinde soru-cevap yapabilen, Retrieval-Augmented Generation (RAG) tabanlı bir analitik platformdur. Türkçe bankacılık düzenlemelerini (BDDK yönetmelikleri vb.) vektör veritabanında indeksleyerek, kullanıcı sorularına ilgili maddelere referans veren yanıtlar üretir.

## Mimari

```
Kullanıcı → FastAPI (/api/v1/ask) → LlamaIndex Query Engine → Qdrant (Hybrid Search) → Ollama (LLM) → Yanıt + Kaynaklar
                                            ↓
                                     MLflow (metrik loglama)
```

**Bileşenler:**

- **FastAPI** — REST API katmanı. Tek endpoint: `POST /api/v1/ask`
- **Qdrant** — Hibrit vektör arama (dense + sparse). Dense vektörler HNSW ile indekslenir.
- **LlamaIndex** — Döküman parçalama, indeksleme, retrieval ve response synthesis orchestration'ı.
- **Ollama (Llama3)** — Lokal çalışan LLM. Yanıt üretimi ve opsiyonel reranking için kullanılır.
- **MLflow** — Deney takibi. Ingestion parametreleri, sorgu latency'leri ve RAGAS değerlendirme metrikleri loglanır.

**Modeller:**

| Görev | Model | Boyut |
|---|---|---|
| Dense Embedding | `intfloat/multilingual-e5-base` | 768 |
| Sparse Embedding | `prithivida/Splade_PP_en_v1` | - |
| LLM | `llama3` (Ollama) | - |

## Gereksinimler

- Docker ve Docker Compose
- Ollama (`ollama serve` ile çalışır durumda olmalı, `ollama pull llama3` ile model indirilmeli)
- Python 3.12+

## Kurulum ve Çalıştırma

### 1. Altyapıyı Ayağa Kaldırma

```bash
docker compose up -d
```

Bu komut üç servis başlatır:

| Servis | Adres |
|---|---|
| Qdrant Dashboard | http://localhost:6333/dashboard |
| MLflow UI | http://localhost:5000 |
| FastAPI (Swagger) | http://localhost:8000/docs |

### 2. Veri İndeksleme

PDF dosyalarını `data/` dizinine koyun. Ardından `Data_Ingestion_and_Indexing.ipynb` notebook'unu çalıştırın. Bu notebook sırasıyla:

1. Qdrant'ta `bank_compliance_v1` koleksiyonunu oluşturur (dense + sparse vektör konfigürasyonu ile).
2. PDF'leri `SimpleDirectoryReader` ile okur, dosya bazlı metadata ekler.
3. `SentenceSplitter` ile chunk'lara ayırır (512 token, 100 overlap).
4. Her chunk'a regex ile madde numarası (`MADDE X`) atar.
5. Hibrit indeksleme yapar (dense: multilingual-e5-base, sparse: Splade).

### 3. Sorgulama

```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Açık bankacılık servisleri nedir?"}'
```

Yanıt formatı:

```json
{
  "answer": "...",
  "sources": [
    {
      "file_name": "BBSEBH.pdf",
      "page_label": "3",
      "article_no": "Madde 4"
    }
  ]
}
```

## Değerlendirme

`Evaluation_and_MLflow.ipynb` notebook'u, 10 adet soru ve ground truth cevabı üzerinden RAGAS framework'ü ile değerlendirme yapar. Ölçülen metrikler:

- **Faithfulness** — Yanıtın, retrieval edilen bağlama sadık kalıp kalmadığı.
- **Answer Relevancy** — Yanıtın soruyla ne kadar ilgili olduğu.

Sonuçlar MLflow'a loglanır. `http://localhost:5000` üzerinden deney bazlı karşılaştırma yapılabilir.

## Proje Yapısı

```
├── app/
│   ├── main.py              # FastAPI uygulama tanımı, lifespan, health check
│   ├── api/
│   │   └── endpoints.py     # /ask endpoint'i, MLflow loglama
│   ├── core/
│   │   └── config.py        # Ortam değişkenleri ve uygulama ayarları
│   ├── models/
│   │   └── schemas.py       # Request/Response Pydantic modelleri
│   └── services/
│       └── rag_service.py   # RAG motoru: Qdrant bağlantı, retrieval, LLM sorgusu
├── data/                     # İndekslenecek PDF dosyaları
├── qdrant_storage/           # Qdrant veri dizini (Docker volume)
├── mlflow_data/              # MLflow veritabanı ve artifact'ler
├── Data_Ingestion_and_Indexing.ipynb
├── Evaluation_and_MLflow.ipynb
├── docker-compose.yaml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Konfigürasyon

Ortam değişkenleri veya `.env` dosyası ile ayarlanabilir:

| Değişken | Varsayılan | Açıklama |
|---|---|---|
| `QDRANT_URL` | `http://localhost:6333` | Qdrant bağlantı adresi |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API adresi |
| `MLFLOW_TRACKING_URI` | `http://localhost:5000` | MLflow sunucu adresi |
| `COLLECTION_NAME` | `bank_compliance_v1` | Qdrant koleksiyon adı |
| `LLM_MODEL_NAME` | `llama3` | Ollama'da kullanılacak model |
| `SIMILARITY_TOP_K` | `5` | Retrieval'da döndürülecek chunk sayısı |

## Notlar

- Ollama, Docker container dışında host makinede çalışır. Container'dan erişim `host.docker.internal` üzerinden sağlanır.
- Embedding modelleri Dockerfile build aşamasında indirilir, runtime'da tekrar indirilmez.
- `rag_service.py` içindeki `LLMRerank` postprocessor'ü şu an devre dışıdır. Etkinleştirmek için ilgili satırlardaki yorumları kaldırın.