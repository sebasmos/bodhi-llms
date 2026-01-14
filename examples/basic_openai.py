"""
Basic example using BODHI with OpenAI.

Before running:
    pip install bodhi[openai]
    export OPENAI_API_KEY="your-key"
"""

import os
from bodhi import BODHI
from bodhi.providers import OpenAIChat


def main():
    # Method 1: Using the OpenAIChat adapter
    chat = OpenAIChat(
        api_key=os.environ.get("OPENAI_API_KEY"),
        model="gpt-4o-mini"
    )
    bodhi = BODHI(chat)

    # Generate a response
    response = bodhi.complete("I've been having headaches for the past week")

    print("=" * 60)
    print("BODHI Response")
    print("=" * 60)
    print("\n📋 ANALYSIS (Pass 1):")
    print("-" * 40)
    print(response.analysis)
    print("\n💬 RESPONSE (Pass 2):")
    print("-" * 40)
    print(response.content)
    print("\n📊 METADATA:")
    print("-" * 40)
    print(f"Mode: {response.metadata.get('mode')}")
    print(f"Domain: {response.metadata.get('domain')}")
    print(f"Total time: {response.metadata.get('total_time', 0):.2f}s")


def example_from_client():
    """Alternative: Create BODHI from an existing OpenAI client."""
    from openai import OpenAI

    client = OpenAI()
    bodhi = BODHI.from_openai(client, model="gpt-4o-mini")

    response = bodhi.complete("What should I do about my persistent cough?")
    print(response.content)


if __name__ == "__main__":
    main()
