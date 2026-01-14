"""
BODHI: Bridging, Open, Discerning, Humble, Inquiring

A lightweight wrapper that embeds epistemic virtues (curiosity and humility)
into LLM responses through a two-pass prompting strategy.

Quick Start:
    from bodhi import BODHI
    from bodhi.providers import OpenAIChat

    chat = OpenAIChat(api_key="sk-...", model="gpt-4o-mini")
    bodhi = BODHI(chat)

    response = bodhi.complete("I have chest pain")
    print(response.content)    # Final response
    print(response.analysis)   # Pass 1 analysis

Or with a simple function:
    from bodhi import BODHI

    def my_chat(messages):
        # Your LLM call here
        return "response"

    bodhi = BODHI(my_chat)
    response = bodhi.complete("Hello")

References:
    - PLOS Digital Health: doi:10.1371/journal.pdig.0001013
    - The Lancet: doi:10.1016/S0140-6736(25)01626-5

License: CC BY-NC-SA 4.0
"""

__version__ = "0.1.0"

from .core import BODHI
from .types import BODHIConfig, BODHIResponse, ChatFunction

__all__ = [
    "BODHI",
    "BODHIConfig",
    "BODHIResponse",
    "ChatFunction",
]
