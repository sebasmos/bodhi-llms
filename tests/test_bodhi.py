"""
Tests for BODHI package.
"""

import pytest
from bodhi import BODHI, BODHIConfig, BODHIResponse


class MockChat:
    """Mock chat function for testing."""

    def __init__(self, responses=None):
        self.responses = responses or ["Analysis response", "Final response"]
        self.call_count = 0
        self.messages_received = []

    def __call__(self, messages):
        self.messages_received.append(messages)
        response = self.responses[min(self.call_count, len(self.responses) - 1)]
        self.call_count += 1
        return response


class TestBODHI:
    """Test BODHI core functionality."""

    def test_init_with_function(self):
        """Test initialization with a simple function."""
        def chat(messages):
            return "Hello"

        bodhi = BODHI(chat)
        assert bodhi.chat == chat
        assert bodhi.config.domain == "medical"

    def test_init_with_config(self):
        """Test initialization with custom config."""
        def chat(messages):
            return "Hello"

        config = BODHIConfig(domain="general")
        bodhi = BODHI(chat, config=config)
        assert bodhi.config.domain == "general"

    def test_two_pass_complete(self):
        """Test two-pass completion mode."""
        mock = MockChat(["Analysis text", "Response text"])
        bodhi = BODHI(mock)

        response = bodhi.complete("Test prompt")

        assert mock.call_count == 2
        assert response.analysis == "Analysis text"
        assert response.content == "Response text"
        assert response.metadata["mode"] == "two_pass"

    def test_single_pass_complete(self):
        """Test single-pass completion mode."""
        mock = MockChat(["Single response"])
        bodhi = BODHI(mock)

        response = bodhi.complete("Test prompt", two_pass=False)

        assert mock.call_count == 1
        assert response.content == "Single response"
        assert response.metadata["mode"] == "single_pass"

    def test_analyze_only(self):
        """Test analyze method (Pass 1 only)."""
        mock = MockChat(["Analysis only"])
        bodhi = BODHI(mock)

        analysis = bodhi.analyze("Test prompt")

        assert mock.call_count == 1
        assert analysis == "Analysis only"

    def test_normalize_string_input(self):
        """Test input normalization with string."""
        mock = MockChat()
        bodhi = BODHI(mock)

        bodhi.complete("  Test prompt  ")

        # Check that the prompt was included in the messages
        messages = mock.messages_received[0]
        assert "Test prompt" in messages[0]["content"]

    def test_normalize_messages_input(self):
        """Test input normalization with message list."""
        mock = MockChat()
        bodhi = BODHI(mock)

        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
            {"role": "user", "content": "How are you?"},
        ]
        bodhi.complete(messages)

        # Check that all content was extracted
        sent_content = mock.messages_received[0][0]["content"]
        assert "Hello" in sent_content
        assert "How are you?" in sent_content

    def test_custom_analysis_template(self):
        """Test custom analysis template."""
        mock = MockChat()
        config = BODHIConfig(analysis_template="Custom: {input}")
        bodhi = BODHI(mock, config=config)

        bodhi.complete("Test")

        messages = mock.messages_received[0]
        assert messages[0]["content"] == "Custom: Test"

    def test_custom_response_template(self):
        """Test custom response template."""
        mock = MockChat(["Analysis", "Response"])
        config = BODHIConfig(
            response_template="Input: {input}\nAnalysis: {analysis}"
        )
        bodhi = BODHI(mock, config=config)

        bodhi.complete("Test")

        # Check Pass 2 message
        messages = mock.messages_received[1]
        assert "Input: Test" in messages[0]["content"]
        assert "Analysis: Analysis" in messages[0]["content"]


class TestBODHIResponse:
    """Test BODHIResponse dataclass."""

    def test_str_returns_content(self):
        """Test that str() returns the content."""
        response = BODHIResponse(
            content="Final answer",
            analysis="Analysis text"
        )
        assert str(response) == "Final answer"

    def test_metadata_defaults_to_empty(self):
        """Test that metadata defaults to empty dict."""
        response = BODHIResponse(content="test", analysis="test")
        assert response.metadata == {}


class TestBODHIConfig:
    """Test BODHIConfig dataclass."""

    def test_defaults(self):
        """Test default configuration values."""
        config = BODHIConfig()
        assert config.analysis_template is None
        assert config.response_template is None
        assert config.domain == "medical"


class TestPrompts:
    """Test prompt generation."""

    def test_medical_domain_prompts(self):
        """Test that medical domain uses medical prompts."""
        mock = MockChat()
        config = BODHIConfig(domain="medical")
        bodhi = BODHI(mock, config=config)

        bodhi.complete("Test")

        messages = mock.messages_received[0]
        assert "medical AI" in messages[0]["content"]

    def test_general_domain_prompts(self):
        """Test that general domain uses general prompts."""
        mock = MockChat()
        config = BODHIConfig(domain="general")
        bodhi = BODHI(mock, config=config)

        bodhi.complete("Test")

        messages = mock.messages_received[0]
        assert "AI assistant" in messages[0]["content"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
