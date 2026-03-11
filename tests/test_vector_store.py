import numpy as np
from unittest.mock import patch, MagicMock
from langchain_core.documents import Document
from services.vector_store import VectorStore


def make_vector_store():
    """Create VectorStore with all heavy models mocked out."""
    with patch("services.vector_store.HuggingFaceEmbeddings") as mock_emb, \
         patch("services.vector_store.CrossEncoder") as mock_ce, \
         patch("services.vector_store.endee") as mock_endee:
        store = VectorStore()
    return store


class TestRerankDocuments:
    def setup_method(self):
        self.store = make_vector_store()

    def test_empty_documents_returns_empty(self):
        results = self.store.rerank_documents("test query", [])
        assert results == []

    def test_documents_ranked_by_score(self):
        docs = [
            Document(page_content="Low relevance text", metadata={"book_name": "A"}),
            Document(page_content="High relevance text", metadata={"book_name": "B"}),
            Document(page_content="Medium relevance text", metadata={"book_name": "C"}),
        ]
        self.store.reranker.predict = MagicMock(return_value=np.array([0.1, 0.9, 0.5]))

        results = self.store.rerank_documents("test query", docs, top_k=3)

        assert len(results) == 3
        assert results[0]["score"] == 0.9
        assert results[0]["metadata"]["book_name"] == "B"
        assert results[1]["score"] == 0.5
        assert results[2]["score"] == 0.1

    def test_top_k_limits_results(self):
        docs = [
            Document(page_content=f"Doc {i}", metadata={})
            for i in range(10)
        ]
        self.store.reranker.predict = MagicMock(
            return_value=np.array([float(i) for i in range(10)])
        )

        results = self.store.rerank_documents("query", docs, top_k=3)
        assert len(results) == 3
        assert results[0]["score"] == 9.0

    def test_result_contains_expected_keys(self):
        docs = [Document(page_content="Test content", metadata={"key": "val"})]
        self.store.reranker.predict = MagicMock(return_value=np.array([0.8]))

        results = self.store.rerank_documents("query", docs, top_k=1)

        assert "content" in results[0]
        assert "metadata" in results[0]
        assert "score" in results[0]
        assert "rank" in results[0]
        assert results[0]["content"] == "Test content"
        assert results[0]["metadata"]["key"] == "val"

    def test_fallback_on_reranker_error(self):
        docs = [
            Document(page_content="Doc A", metadata={}),
            Document(page_content="Doc B", metadata={}),
        ]
        self.store.reranker.predict = MagicMock(side_effect=RuntimeError("model error"))

        results = self.store.rerank_documents("query", docs, top_k=2)

        assert len(results) == 2
        assert all(r["score"] == 0.5 for r in results)
