from unittest.mock import patch, MagicMock
from services.llm_service import LLMService


def make_service():
    """Create LLMService with mocked Groq client."""
    with patch("services.llm_service.Groq"):
        return LLMService()


class TestCreatePrompt:
    def setup_method(self):
        self.service = make_service()

    def test_beginner_mode_contains_beginner_instructions(self):
        docs = [{
            "content": "Dharma is righteous duty.",
            "metadata": {"book_name": "Bhagavad Gita", "chapter": "1", "section": ""}
        }]
        prompt = self.service.create_prompt("What is dharma?", docs, "beginner")
        assert "beginner" in prompt.lower()
        assert "What is dharma?" in prompt
        assert "Dharma is righteous duty." in prompt
        assert "Bhagavad Gita" in prompt

    def test_expert_mode_contains_scholarly_instructions(self):
        docs = [{
            "content": "Dharma is righteous duty.",
            "metadata": {"book_name": "Bhagavad Gita", "chapter": "1", "section": ""}
        }]
        prompt = self.service.create_prompt("What is dharma?", docs, "expert")
        assert "scholarly" in prompt.lower()
        assert "What is dharma?" in prompt

    def test_multiple_docs_all_included(self):
        docs = [
            {"content": "First doc.", "metadata": {"book_name": "Book A", "chapter": "", "section": ""}},
            {"content": "Second doc.", "metadata": {"book_name": "Book B", "chapter": "", "section": ""}},
        ]
        prompt = self.service.create_prompt("test", docs, "beginner")
        assert "First doc." in prompt
        assert "Second doc." in prompt
        assert "Book A" in prompt
        assert "Book B" in prompt


class TestExtractCitations:
    def setup_method(self):
        self.service = make_service()

    def test_extracts_citation_fields(self):
        docs = [{
            "content": "Dharma is the foundation of all order in the universe and society.",
            "metadata": {
                "book_name": "Bhagavad Gita",
                "chapter": "3",
                "section": "Karma Yoga",
                "verse_number": "35"
            }
        }]
        citations = self.service.extract_citations(docs)
        assert len(citations) == 1
        assert citations[0]["book"] == "Bhagavad Gita"
        assert citations[0]["chapter"] == "3"
        assert citations[0]["section"] == "Karma Yoga"
        assert citations[0]["verse"] == "35"
        assert citations[0]["content_preview"].endswith("...")

    def test_missing_metadata_uses_defaults(self):
        docs = [{"content": "Some text here.", "metadata": {}}]
        citations = self.service.extract_citations(docs)
        assert citations[0]["book"] == "Unknown Source"
        assert citations[0]["chapter"] == ""

    def test_empty_docs_returns_empty(self):
        assert self.service.extract_citations([]) == []


class TestGetBookRecommendations:
    def setup_method(self):
        self.service = make_service()

    def test_returns_unique_books(self):
        docs = [
            {"metadata": {"book_name": "Bhagavad Gita"}},
            {"metadata": {"book_name": "Bhagavad Gita"}},
            {"metadata": {"book_name": "Mahabharata"}},
        ]
        recs = self.service.get_book_recommendations(docs)
        assert len(recs) == 2
        assert "Bhagavad Gita" in recs
        assert "Mahabharata" in recs

    def test_max_three_recommendations(self):
        docs = [
            {"metadata": {"book_name": f"Book {i}"}}
            for i in range(10)
        ]
        recs = self.service.get_book_recommendations(docs)
        assert len(recs) <= 3

    def test_empty_docs_returns_empty(self):
        assert self.service.get_book_recommendations([]) == []

    def test_missing_book_name_skipped(self):
        docs = [
            {"metadata": {}},
            {"metadata": {"book_name": "Ramayana"}},
        ]
        recs = self.service.get_book_recommendations(docs)
        assert "Ramayana" in recs
