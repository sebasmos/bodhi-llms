"""
BODHI Core - Two-Pass Epistemic Virtues Framework.

This module implements the core BODHI logic: a two-pass prompting strategy
that embeds curiosity and humility into LLM responses.

Reference: PLOS Digital Health (doi: 10.1371/journal.pdig.0001013)
"""

from typing import Any, Callable, Dict, List, Optional, Union
import time

from .types import BODHIConfig, BODHIResponse, ChatFunction, Messages
from .prompts import render_analysis_prompt, render_response_prompt


class BODHI:
    """
    BODHI: Bridging, Open, Discerning, Humble, Inquiring.

    A lightweight wrapper that embeds epistemic virtues into LLM responses
    through a two-pass prompting strategy.

    Example:
        from bodhi import BODHI
        from bodhi.providers import OpenAIChat

        chat = OpenAIChat(api_key="sk-...", model="gpt-4o-mini")
        bodhi = BODHI(chat)

        response = bodhi.complete("I have chest pain")
        print(response.content)    # Final response
        print(response.analysis)   # Pass 1 analysis
    """

    def __init__(
        self,
        chat_function: ChatFunction,
        config: Optional[BODHIConfig] = None,
    ):
        """
        Initialize BODHI with a chat function.

        Args:
            chat_function: Any callable that takes messages and returns a string.
                          Can be a provider adapter or a simple function.
            config: Optional configuration for prompts and behavior.
        """
        self.chat = chat_function
        self.config = config or BODHIConfig()

    @classmethod
    def from_openai(
        cls,
        client: Any,
        model: str = "gpt-4o-mini",
        **kwargs
    ) -> "BODHI":
        """
        Create BODHI from an OpenAI client (convenience method).

        Args:
            client: OpenAI client instance
            model: Model to use (default: gpt-4o-mini)
            **kwargs: Additional arguments passed to BODHIConfig

        Returns:
            BODHI instance configured with OpenAI
        """
        from .providers.openai import OpenAIChat
        chat = OpenAIChat(client=client, model=model)
        config = BODHIConfig(**kwargs) if kwargs else None
        return cls(chat, config)

    def complete(
        self,
        prompt: Union[str, Messages],
        two_pass: bool = True,
    ) -> BODHIResponse:
        """
        Generate a response with BODHI enhancement.

        Args:
            prompt: User prompt (string or list of messages)
            two_pass: If True (default), use two-pass mode. If False, single pass.

        Returns:
            BODHIResponse with content, analysis, and metadata
        """
        # Normalize input to string
        case_text = self._normalize_input(prompt)

        if two_pass:
            return self._two_pass(case_text)
        else:
            return self._single_pass(case_text)

    def analyze(self, prompt: Union[str, Messages]) -> str:
        """
        Run only Pass 1 (analysis) without generating a response.

        Useful for debugging or understanding how BODHI interprets a case.

        Args:
            prompt: User prompt

        Returns:
            The analysis text
        """
        case_text = self._normalize_input(prompt)
        analysis_prompt = self._get_analysis_prompt(case_text)
        messages = [{"role": "user", "content": analysis_prompt}]
        return self.chat(messages)

    def _two_pass(self, case_text: str) -> BODHIResponse:
        """
        Execute the two-pass BODHI strategy.

        Pass 1: Analyze the case with intellectual humility
        Pass 2: Generate response incorporating insights from analysis
        """
        start_time = time.time()

        # Pass 1: Analysis
        analysis_prompt = self._get_analysis_prompt(case_text)
        analysis_messages = [{"role": "user", "content": analysis_prompt}]
        analysis = self.chat(analysis_messages)

        pass1_time = time.time() - start_time

        # Pass 2: Response
        response_prompt = self._get_response_prompt(case_text, analysis)
        response_messages = [{"role": "user", "content": response_prompt}]
        content = self.chat(response_messages)

        total_time = time.time() - start_time

        return BODHIResponse(
            content=content,
            analysis=analysis,
            metadata={
                "mode": "two_pass",
                "domain": self.config.domain,
                "pass1_time": pass1_time,
                "total_time": total_time,
            }
        )

    def _single_pass(self, case_text: str) -> BODHIResponse:
        """
        Execute single-pass mode (analysis embedded in response).
        """
        start_time = time.time()

        # Use analysis prompt but expect direct response
        analysis_prompt = self._get_analysis_prompt(case_text)
        messages = [{"role": "user", "content": analysis_prompt}]
        content = self.chat(messages)

        return BODHIResponse(
            content=content,
            analysis="(Single-pass mode - analysis embedded in response)",
            metadata={
                "mode": "single_pass",
                "domain": self.config.domain,
                "total_time": time.time() - start_time,
            }
        )

    def _normalize_input(self, prompt: Union[str, Messages]) -> str:
        """Convert various input formats to plain text."""
        if isinstance(prompt, str):
            return prompt.strip()

        if isinstance(prompt, list):
            parts = []
            for msg in prompt:
                if not isinstance(msg, dict):
                    continue
                content = msg.get("content", "")
                if isinstance(content, list):
                    for part in content:
                        if isinstance(part, dict) and part.get("type") == "text":
                            parts.append(str(part.get("text", "")))
                elif isinstance(content, str):
                    parts.append(content)
            return "\n".join(p for p in parts if p).strip()

        return str(prompt)

    def _get_analysis_prompt(self, case_text: str) -> str:
        """Get the analysis prompt (custom or default)."""
        if self.config.analysis_template:
            return self.config.analysis_template.format(input=case_text)
        return render_analysis_prompt(case_text, self.config.domain)

    def _get_response_prompt(self, case_text: str, analysis: str) -> str:
        """Get the response prompt (custom or default)."""
        if self.config.response_template:
            return self.config.response_template.format(input=case_text, analysis=analysis)
        return render_response_prompt(case_text, analysis, self.config.domain)
