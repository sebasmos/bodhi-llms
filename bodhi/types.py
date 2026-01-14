"""
BODHI Types and Protocols.

Defines the core abstractions for provider-agnostic LLM communication.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Protocol, Optional, Union


class ChatFunction(Protocol):
    """
    Protocol for any function that takes messages and returns a string response.

    This is the only interface BODHI needs from any LLM provider.
    Any callable that matches this signature will work.

    Example:
        def my_chat(messages: List[Dict[str, str]]) -> str:
            return "Hello!"

        bodhi = BODHI(my_chat)
    """
    def __call__(self, messages: List[Dict[str, str]]) -> str: ...


@dataclass
class BODHIResponse:
    """
    Response from BODHI containing both the final response and analysis.

    Attributes:
        content: The final response text (Pass 2 output)
        analysis: The Pass 1 analysis (structured reflection)
        metadata: Additional information (timing, tokens, etc.)
    """
    content: str
    analysis: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return self.content


@dataclass
class BODHIConfig:
    """
    Configuration for BODHI behavior.

    Attributes:
        analysis_template: Custom template for Pass 1 (analysis)
        response_template: Custom template for Pass 2 (response)
        domain: Preset domain for prompts ("medical", "general", etc.)
    """
    analysis_template: Optional[str] = None
    response_template: Optional[str] = None
    domain: str = "medical"


# Type aliases for clarity
Messages = List[Dict[str, str]]
MessageContent = Union[str, List[Dict[str, Any]]]
