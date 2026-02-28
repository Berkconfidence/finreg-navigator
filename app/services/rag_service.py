from qdrant_client import QdrantClient
from llama_index.core import VectorStoreIndex, PromptTemplate
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import LLMRerank
from app.core.config import settings
from app.models.schemas import QueryResponse, SourceNodeMetadata

class BankingRAGService:
    def __init__(self):
        self.client = QdrantClient(url=settings.QDRANT_URL)
        
        self.embed_model = HuggingFaceEmbedding(model_name=settings.EMBED_MODEL_NAME)
        
        self.llm = Ollama(
            model=settings.LLM_MODEL_NAME,
            base_url=settings.OLLAMA_BASE_URL,
            request_timeout=120.0,
            additional_kwargs={"keep_alive": 0}
        )
        
        self.query_engine = self._setup_engine()

    def _setup_engine(self):
        """RAG mimarisini kurar."""
        vector_store = QdrantVectorStore(
            collection_name=settings.COLLECTION_NAME,
            client=self.client,
            enable_hybrid=True,
            dense_vector_name="dense",
            sparse_vector_name="sparse"
        )
        
        index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store, 
            embed_model=self.embed_model
        )

        qa_prompt_tmpl = PromptTemplate(
            "SADECE SANA VERİLEN BAĞLAMDAKİ BİLGİLERİ KULLANARAK CEVAP VER.\n"
            "KESİNLİKLE TÜRKÇE DIŞINDA BİR DİL KULLANMA.\n"
            "Sen kıdemli bir Bankacılık Uyum Analistisin. Cevabını verirken mutlaka hangi maddeye dayandığını belirt.\n"
            "BAĞLAM:\n{context_str}\n"
            "SORU: {query_str}\n"
            "YANIT (SADECE TÜRKÇE): "
        )

        base_retriever = index.as_retriever(similarity_top_k=settings.SIMILARITY_TOP_K)
        # reranker = LLMRerank(choice_batch_size=5, top_n=3, llm=self.llm)

        engine = RetrieverQueryEngine.from_args(
            base_retriever, 
            llm=self.llm,
            # node_postprocessors=[reranker]
        )
        engine.update_prompts({"response_synthesizer:text_qa_template": qa_prompt_tmpl})
        
        return engine

    def ask_question(self, question: str) -> QueryResponse:
        """Kullanıcı sorusuna RAG yanıtı üretir."""
        response = self.query_engine.query(question)
        
        sources = [
            SourceNodeMetadata(
                file_name=node.node.metadata.get("file_name", "Bilinmiyor"),
                page_label=node.node.metadata.get("page_label", "0"),
                article_no=node.node.metadata.get("article_no", "Belirtilmemiş")
            )
            for node in response.source_nodes
        ]
        
        return QueryResponse(
            answer=str(response),
            sources=sources
        )

_rag_service = None

def get_rag_service() -> BankingRAGService:
    """Lazy initialization - ilk çağrıda servisi oluşturur."""
    global _rag_service
    if _rag_service is None:
        _rag_service = BankingRAGService()
    return _rag_service