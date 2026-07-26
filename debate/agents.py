import re

MAX_SENTENCES = 5

# Each of the 4 debaters is a different low/no-cost provider on purpose --
# this is meant as an exercise in comparing cheap models against each other.
# Swap models/providers freely; call_llm() only needs a provider key that
# exists in providers._PROVIDER_CONFIG plus a valid model name for it.
AGENT_CONFIG = {
    "A1": {"provider": "groq", "model": "llama-3.3-70b-versatile", "side": "A"},
    "A2": {"provider": "openrouter", "model": "meta-llama/llama-3.1-8b-instruct:free", "side": "A"},
    "B1": {"provider": "gemini", "model": "gemini-2.5-flash", "side": "B"},
    "B2": {"provider": "openai", "model": "gpt-5.4-mini", "side": "B"},
    "JUDGE": {"provider": "gemini", "model": "gemini-2.5-flash", "side": None},
}

# Debater 1 on each side opens and closes; debater 2 argues the middle turn.
TURN_ORDER = ["A1", "B1", "A2", "B2", "A1", "B1"]

SIDE_LABEL = {"A": "Side A", "B": "Side B"}


def trim_to_sentences(text: str, max_sentences: int = MAX_SENTENCES) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return " ".join(s for s in sentences[:max_sentences] if s).strip()
