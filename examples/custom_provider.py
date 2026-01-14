"""
Example: Using BODHI with a custom provider.

BODHI works with ANY function that takes messages and returns a string.
This example shows how to create custom providers.
"""

from typing import List, Dict
from bodhi import BODHI


# Example 1: Simple function
def echo_chat(messages: List[Dict[str, str]]) -> str:
    """Simple echo chat for testing."""
    last_message = messages[-1]["content"]
    return f"Echo: {last_message[:100]}..."


# Example 2: Class-based provider
class OllamaChat:
    """Example Ollama provider (not implemented - for illustration)."""

    def __init__(self, model: str = "llama3.2", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def __call__(self, messages: List[Dict[str, str]]) -> str:
        """
        In a real implementation, this would call the Ollama API.

        import httpx
        response = httpx.post(
            f"{self.base_url}/api/chat",
            json={"model": self.model, "messages": messages}
        )
        return response.json()["message"]["content"]
        """
        # Placeholder for demonstration
        return "Ollama response would go here"


# Example 3: Wrapper around any API
class AnthropicChat:
    """Example Anthropic provider (not implemented - for illustration)."""

    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        self.api_key = api_key
        self.model = model

    def __call__(self, messages: List[Dict[str, str]]) -> str:
        """
        In a real implementation:

        from anthropic import Anthropic
        client = Anthropic(api_key=self.api_key)
        response = client.messages.create(
            model=self.model,
            messages=messages,
            max_tokens=1024
        )
        return response.content[0].text
        """
        return "Anthropic response would go here"


def main():
    # Use the simple echo function
    bodhi = BODHI(echo_chat)

    response = bodhi.complete("Hello, how are you?")
    print("Echo provider response:")
    print(response.content)
    print()

    # Use a class-based provider
    ollama = OllamaChat(model="llama3.2")
    bodhi_ollama = BODHI(ollama)

    response = bodhi_ollama.complete("What is the weather like?")
    print("Ollama provider response:")
    print(response.content)


if __name__ == "__main__":
    main()
