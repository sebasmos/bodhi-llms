"""
BODHI Provider Adapters.

Pre-built adapters for common LLM providers. Each adapter implements
the ChatFunction protocol (messages -> string).
"""

from .openai import OpenAIChat

__all__ = ["OpenAIChat"]
