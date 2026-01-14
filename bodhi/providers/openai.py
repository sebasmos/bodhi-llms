"""
OpenAI Provider Adapter for BODHI.

Provides a simple adapter that wraps the OpenAI client to match
the ChatFunction protocol.
"""

from typing import Any, Dict, List, Optional


class OpenAIChat:
    """
    OpenAI adapter for BODHI.

    Wraps an OpenAI client to provide the ChatFunction interface.

    Example:
        from openai import OpenAI
        from bodhi.providers import OpenAIChat

        client = OpenAI()
        chat = OpenAIChat(client=client, model="gpt-4o-mini")

        # Or with API key directly
        chat = OpenAIChat(api_key="sk-...", model="gpt-4o-mini")
    """

    def __init__(
        self,
        client: Optional[Any] = None,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ):
        """
        Initialize OpenAI adapter.

        Args:
            client: Existing OpenAI client instance
            api_key: OpenAI API key (used if client not provided)
            model: Model to use (default: gpt-4o-mini)
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
        """
        if client is not None:
            self.client = client
        elif api_key is not None:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=api_key)
            except ImportError:
                raise ImportError(
                    "OpenAI package not installed. Install with: pip install openai"
                )
        else:
            # Try to create client from environment
            try:
                from openai import OpenAI
                self.client = OpenAI()
            except ImportError:
                raise ImportError(
                    "OpenAI package not installed. Install with: pip install openai"
                )

        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def __call__(self, messages: List[Dict[str, str]]) -> str:
        """
        Call the OpenAI API with the given messages.

        Args:
            messages: List of message dicts with 'role' and 'content'

        Returns:
            The assistant's response text
        """
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
        }
        if self.max_tokens:
            kwargs["max_tokens"] = self.max_tokens

        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content or ""
