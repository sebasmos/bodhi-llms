# BODHI: Bridging, Open, Discerning, Humble, Inquiring

[![PyPI](https://img.shields.io/pypi/v/bodhi-llm)](https://pypi.org/project/bodhi-llm/)
[![PLOS Digital Health](https://img.shields.io/badge/PLOS_Digital_Health-10.1371/journal.pdig.0001013-blue)](https://journals.plos.org/digitalhealth/article?id=10.1371/journal.pdig.0001013)
[![The Lancet](https://img.shields.io/badge/The_Lancet-10.1016/S0140--6736(25)01626--5-red)](https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(25)01626-5/fulltext)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC_BY--NC--SA_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

A lightweight, provider-agnostic wrapper that embeds **epistemic virtues** (curiosity and humility) into LLM responses through a two-pass prompting strategy.

## Installation

### From PyPI

```bash
pip install bodhi-llm

# With OpenAI support
pip install bodhi-llm[openai]

# All providers
pip install bodhi-llm[all]
```

### From Source (for development)

```bash
# Clone the repository
git clone https://github.com/sebasmos/bodhi.git
cd bodhi

# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip (required for editable install with pyproject.toml)
pip install --upgrade pip

# Install with all dependencies
pip install -e ".[all]"

# Or install with dev dependencies for testing
pip install -e ".[dev]"
```

## Quick Start

### With OpenAI

```python
from bodhi import BODHI
from bodhi.providers import OpenAIChat

# Create chat function
chat = OpenAIChat(api_key="sk-...", model="gpt-4o-mini")

# Wrap with BODHI
bodhi = BODHI(chat)

# Generate response
response = bodhi.complete("I have chest pain")
print(response.content)    # Final response
print(response.analysis)   # Pass 1 analysis
```

### With Any Provider (Custom Function)

BODHI works with any function that takes messages and returns a string:

```python
from bodhi import BODHI

def my_chat(messages):
    """Your custom LLM call - just return a string."""
    # Call your API, local model, whatever
    return "response text"

bodhi = BODHI(my_chat)
response = bodhi.complete("I have chest pain")
```

### Direct from OpenAI Client

```python
from bodhi import BODHI
from openai import OpenAI

client = OpenAI()
bodhi = BODHI.from_openai(client, model="gpt-4o-mini")

response = bodhi.complete("I have chest pain")
```

## How It Works

BODHI uses a **two-pass prompting strategy**:

```
Pass 1: Analysis
  Input: User prompt
  Output: Structured reflection containing:
    - WHAT I THINK (assessment)
    - WHAT I'M UNSURE ABOUT (uncertainties)
    - WHAT I NEED TO KNOW (questions)
    - RED FLAGS (safety concerns)
    - SAFE ADVICE (confident recommendations)

Pass 2: Response
  Input: Original prompt + Pass 1 analysis
  Output: Natural response that:
    - ASKS identified questions
    - EXPRESSES identified uncertainties
    - INCLUDES safety warnings
    - PROVIDES safe recommendations
```

### Why It Works

| Aspect | Baseline | BODHI |
|--------|----------|-------|
| **Uncertainty** | Often overconfident | Appropriately humble |
| **Missing info** | Makes assumptions | Asks clarifying questions |
| **Safety** | May miss red flags | Explicitly considers red flags |
| **Recommendations** | Generic advice | Contextually appropriate advice |

## Configuration

### Custom Prompts

```python
from bodhi import BODHI, BODHIConfig

config = BODHIConfig(
    analysis_template="Analyze this: {input}",
    response_template="Respond to: {input}\nUsing analysis: {analysis}",
    domain="general"  # or "medical" (default)
)

bodhi = BODHI(chat, config=config)
```

### Single-Pass Mode

```python
# For comparison or speed
response = bodhi.complete("prompt", two_pass=False)
```

### Analysis Only

```python
# Debug or inspect the analysis
analysis = bodhi.analyze("I have chest pain")
print(analysis)
```

## API Reference

### `BODHI`

Main class for BODHI functionality.

```python
BODHI(
    chat_function: ChatFunction,  # Any callable: messages -> str
    config: Optional[BODHIConfig] = None
)
```

**Methods:**
- `complete(prompt, two_pass=True)` - Generate response with BODHI enhancement
- `analyze(prompt)` - Run only Pass 1 (analysis)
- `from_openai(client, model)` - Create from OpenAI client (class method)

### `BODHIResponse`

Response object returned by `complete()`.

```python
@dataclass
class BODHIResponse:
    content: str      # Final response text
    analysis: str     # Pass 1 analysis
    metadata: dict    # Timing, domain, etc.
```

### `BODHIConfig`

Configuration for BODHI behavior.

```python
@dataclass
class BODHIConfig:
    analysis_template: Optional[str] = None  # Custom Pass 1 prompt
    response_template: Optional[str] = None  # Custom Pass 2 prompt
    domain: str = "medical"                  # "medical" or "general"
```

## Provider Adapters

### OpenAI

```python
from bodhi.providers import OpenAIChat

chat = OpenAIChat(
    api_key="sk-...",           # Or use OPENAI_API_KEY env var
    model="gpt-4o-mini",
    temperature=0.7,
    max_tokens=None
)
```

### Custom Provider

Implement the `ChatFunction` protocol:

```python
from typing import List, Dict

def my_chat(messages: List[Dict[str, str]]) -> str:
    # Your implementation
    return "response"

# Or as a class
class MyChat:
    def __call__(self, messages: List[Dict[str, str]]) -> str:
        return "response"
```

## Citation

If you use BODHI in your research, please cite:

```bibtex
@article{cajas2026beyond,
  title={Beyond overconfidence: Embedding curiosity and humility for ethical medical AI},
  author={Cajas Ordóñez, Sebastián Andrés and Castro, Rowell and Celi, Leo Anthony and Delos Reyes, Roben and Engelmann, Justin and Ercole, Ari and Hilel, Almog and Kalla, Mahima and Kinyera, Leo and Lange, Maximin and others},
  journal={PLOS Digital Health},
  volume={5},
  number={1},
  pages={e0001013},
  year={2026},
  publisher={Public Library of Science San Francisco, CA USA}
}

@article{ordonez2025humility,
  title={Humility and curiosity in human--AI systems for health care},
  author={Ordoñez, Sebastián Andrés Cajas and Lange, Maximin and Lunde, Torleif Markussen and Meni, Mackenzie J and Premo, Anna E},
  journal={The Lancet},
  volume={406},
  number={10505},
  pages={804--805},
  year={2025},
  publisher={Elsevier}
}
```

## License

CC BY-NC-SA 4.0 - See [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Please read the contributing guidelines and submit PRs.

## Links

- [PLOS Digital Health Paper](https://journals.plos.org/digitalhealth/article?id=10.1371/journal.pdig.0001013)
- [The Lancet Commentary](https://www.thelancet.com/journals/lancet/article/PIIS0140-6736(25)01626-5/fulltext)
- [HumbleAILLMs Repository](https://github.com/sebasmos/HumbleAILLMs)
