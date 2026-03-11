from services.chat_service import ChatService


class TestGenerateSessionTitle:
    def setup_method(self):
        self.service = ChatService()

    def test_short_message(self):
        title = self.service.generate_session_title("What is dharma?")
        assert title == "What is dharma?"

    def test_long_message_truncates_at_word_boundary(self):
        long_msg = "This is a very long question about the nature of dharma and karma in Hindu philosophy and scriptures"
        title = self.service.generate_session_title(long_msg)
        assert len(title) <= 54  # 50 chars + "..."
        assert title.endswith("...")

    def test_empty_message_returns_default(self):
        title = self.service.generate_session_title("")
        assert title == "New Chat"

    def test_whitespace_only_returns_default(self):
        title = self.service.generate_session_title("   ")
        assert title == "New Chat"

    def test_newlines_cleaned(self):
        title = self.service.generate_session_title("Hello\nWorld\nTest")
        assert "\n" not in title
        assert title == "Hello World Test"

    def test_extra_spaces_collapsed(self):
        title = self.service.generate_session_title("Hello    World")
        assert title == "Hello World"

    def test_exactly_50_chars_not_truncated(self):
        msg = "a" * 50
        title = self.service.generate_session_title(msg)
        assert title == msg
        assert "..." not in title

    def test_51_chars_truncated(self):
        msg = "a" * 51
        title = self.service.generate_session_title(msg)
        assert title.endswith("...")
