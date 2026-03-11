import json
import tempfile
from pathlib import Path
from langchain_core.documents import Document
from services.document_processor import DocumentProcessor


class TestChunkDocuments:
    def setup_method(self):
        self.processor = DocumentProcessor(chunk_size=50, chunk_overlap=10)

    def test_short_doc_stays_single_chunk(self):
        docs = [Document(page_content="Short text.", metadata={"book_name": "Test"})]
        chunks = self.processor.chunk_documents(docs)
        assert len(chunks) >= 1
        assert chunks[0].metadata["book_name"] == "Test"
        assert "chunk_id" in chunks[0].metadata

    def test_long_doc_splits_into_multiple_chunks(self):
        long_text = "This is a sentence. " * 50
        docs = [Document(page_content=long_text, metadata={"book_name": "Test"})]
        chunks = self.processor.chunk_documents(docs)
        assert len(chunks) > 1
        for chunk in chunks:
            assert chunk.metadata["book_name"] == "Test"
            assert "chunk_id" in chunk.metadata
            assert "total_chunks" in chunk.metadata

    def test_empty_doc_list(self):
        chunks = self.processor.chunk_documents([])
        assert chunks == []

    def test_metadata_preserved_across_chunks(self):
        docs = [Document(
            page_content="Word " * 100,
            metadata={"book_name": "Gita", "chapter": "2"}
        )]
        chunks = self.processor.chunk_documents(docs)
        for chunk in chunks:
            assert chunk.metadata["book_name"] == "Gita"
            assert chunk.metadata["chapter"] == "2"


class TestLoadJsonlDocuments:
    def setup_method(self):
        self.processor = DocumentProcessor()

    def test_loads_valid_jsonl(self):
        records = [
            {"content": "First passage.", "metadata": {"book_name": "Book A"}},
            {"content": "Second passage.", "metadata": {"book_name": "Book B"}},
        ]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            for record in records:
                f.write(json.dumps(record) + "\n")
            tmp_path = f.name

        docs = self.processor.load_jsonl_documents(tmp_path)
        assert len(docs) == 2
        assert docs[0].page_content == "First passage."
        assert docs[0].metadata["book_name"] == "Book A"
        assert docs[1].page_content == "Second passage."

        Path(tmp_path).unlink()

    def test_empty_jsonl_returns_empty(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            tmp_path = f.name

        docs = self.processor.load_jsonl_documents(tmp_path)
        assert docs == []

        Path(tmp_path).unlink()
