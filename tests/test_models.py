import pytest
from pydantic import ValidationError
from models.database import QueryRequest, ChatMessage, UserCreate


class TestQueryRequest:
    def test_valid_request(self):
        req = QueryRequest(query="What is karma?")
        assert req.query == "What is karma?"
        assert req.mode == "beginner"
        assert req.session_id is None

    def test_expert_mode(self):
        req = QueryRequest(query="Explain atman", mode="expert")
        assert req.mode == "expert"

    def test_with_session_id(self):
        req = QueryRequest(query="Tell me more", session_id="abc123")
        assert req.session_id == "abc123"

    def test_missing_query_raises(self):
        with pytest.raises(ValidationError):
            QueryRequest()


class TestChatMessage:
    def test_valid_message(self):
        msg = ChatMessage(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert msg.mode == "beginner"
        assert msg.timestamp is not None

    def test_assistant_message_with_citations(self):
        msg = ChatMessage(
            role="assistant",
            content="Dharma means duty.",
            citations=[{"book": "Gita", "chapter": "3"}],
            hindi_translation="धर्म का अर्थ कर्तव्य है।"
        )
        assert msg.role == "assistant"
        assert len(msg.citations) == 1
        assert msg.hindi_translation == "धर्म का अर्थ कर्तव्य है।"

    def test_missing_required_fields_raises(self):
        with pytest.raises(ValidationError):
            ChatMessage(role="user")


class TestUserCreate:
    def test_valid_user(self):
        user = UserCreate(
            email="test@example.com",
            password="secret123",
            full_name="Test User"
        )
        assert user.email == "test@example.com"
        assert user.preferred_mode == "beginner"

    def test_invalid_email_raises(self):
        with pytest.raises(ValidationError):
            UserCreate(
                email="not-an-email",
                password="secret123",
                full_name="Test User"
            )

    def test_expert_mode(self):
        user = UserCreate(
            email="guru@example.com",
            password="secret123",
            full_name="Guru",
            preferred_mode="expert"
        )
        assert user.preferred_mode == "expert"
