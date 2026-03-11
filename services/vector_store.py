# services/vector_store.py

import uuid
import logging
from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from sentence_transformers import CrossEncoder
from config.config import Config
import endee
from endee import Precision


logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self):
        # Initialize embeddings model
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=Config.EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'}
        )

        # Initialize cross-encoder for reranking
        self.reranker = CrossEncoder(Config.RERANKER_MODEL)

        # Endee client configuration
        self.client = endee.Endee()
        self.client.set_base_url(f"{Config.ENDEE_HOST}{Config.ENDEE_API_PREFIX}")
        self.index_name = Config.ENDEE_INDEX_NAME

        self._index = None

    @property
    def index(self):
        """Lazy load the index"""
        if self._index is None:
            self._index = self.client.get_index(name=self.index_name)
        return self._index

    async def initialize_vectorstore(self):
        """Initialize the Endee index"""
        try:
            # Check if index exists
            indexes = self.client.list_indexes()
            index_names = [idx['name'] for idx in indexes.get('indexes', [])]

            if self.index_name not in index_names:
                self.client.create_index(
                    name=self.index_name,
                    dimension=384,
                    space_type='cosine',
                    precision=Precision.FLOAT32
                )
                logger.info(f"Index '{self.index_name}' created successfully")
            else:
                logger.info(f"Index '{self.index_name}' already exists")

            # Refresh the index reference
            self._index = self.client.get_index(name=self.index_name)
            logger.info("Vector store initialized successfully")
            return {"status": "success"}

        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            return {"error": str(e)}

    async def add_documents(self, documents: List[Document], batch_size: int = 50):
        """Add documents to Endee vector store"""
        try:
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                vectors = []

                for j, doc in enumerate(batch):
                    # Embed the page_content
                    embedded_vector = self.embedding_model.embed_query(doc.page_content)

                    # Hide page_content inside metadata since Endee only accepts metadata dicts
                    metadata_dict = dict(doc.metadata)
                    metadata_dict["page_content"] = doc.page_content

                    vectors.append({
                        "id": str(uuid.uuid4()),
                        "vector": embedded_vector,
                        "meta": metadata_dict
                    })

                # Upsert to Endee
                self.index.upsert(vectors)

                logger.info(f"Added batch {i // batch_size + 1} of {(len(documents) + batch_size - 1) // batch_size}")

            logger.info(f"Added {len(documents)} documents to vector store")

        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            raise

    async def similarity_search(self, query: str, k: int = Config.TOP_K_RETRIEVAL) -> List[Document]:
        """Perform similarity search"""
        try:
            # Embed the query
            query_vector = self.embedding_model.embed_query(query)

            # Search Endee
            results = self.index.query(
                vector=query_vector,
                top_k=k
            )

            documents = []
            for result in results:
                metadata = dict(result.get('meta', {}))
                page_content = metadata.pop("page_content", "")

                documents.append(Document(
                    page_content=page_content,
                    metadata=metadata
                ))

            logger.info(f"Retrieved {len(documents)} documents for query")
            return documents

        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            raise

    def rerank_documents(self, query: str, documents: List[Document], top_k: int = Config.TOP_K_RERANK) -> List[Dict[str, Any]]:
        """Rerank documents using cross-encoder"""
        try:
            if not documents:
                return []

            pairs = [(query, doc.page_content) for doc in documents]
            scores = self.reranker.predict(pairs)

            results = [
                {
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'score': float(score),
                    'rank': i + 1
                }
                for i, (doc, score) in enumerate(zip(documents, scores))
            ]

            results = sorted(results, key=lambda x: x['score'], reverse=True)
            return results[:top_k]

        except Exception as e:
            logger.error(f"Error in reranking: {e}")
            return [
                {
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'score': 0.5,
                    'rank': i + 1
                }
                for i, doc in enumerate(documents[:top_k])
            ]

    async def search_and_rerank(self, query: str) -> List[Dict[str, Any]]:
        """Combined search and rerank pipeline"""
        try:
            initial_results = await self.similarity_search(query, Config.TOP_K_RETRIEVAL)
            return self.rerank_documents(query, initial_results, Config.TOP_K_RERANK)
        except Exception as e:
            logger.error(f"Error in search and rerank: {e}")
            raise

    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        try:
            indexes = self.client.list_indexes()
            index_list = indexes.get('indexes', [])

            stats = None
            for idx in index_list:
                if idx['name'] == self.index_name:
                    stats = idx
                    break

            if not stats:
                return {"error": f"Index '{self.index_name}' not found"}

            return {
                "index_name": self.index_name,
                "total_documents": stats.get("total_elements", 0),
                "embedding_model": Config.EMBEDDING_MODEL,
                "reranker_model": Config.RERANKER_MODEL
            }

        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {"error": str(e)}

    async def reset_vectorstore(self):
        """Delete the existing Endee index and reset"""
        try:
            self.client.delete_index(name=self.index_name)
            logger.warning(f"Index '{self.index_name}' deleted")
            self._index = None
            await self.initialize_vectorstore()

        except Exception as e:
            logger.error(f"Error resetting vector store: {e}")
            raise
