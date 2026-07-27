import re

MAX_SENTENCES = 5

# Each of the 4 debaters is a different low/no-cost provider on purpose --
# this is meant as an exercise in comparing cheap models against each other.
# JUDGE deliberately uses a provider/model that NO debater uses (DeepSeek) --
# a judge that shares a model with one of the debaters is not neutral.
# Swap models/providers freely; call_llm() only needs a provider key that
# exists in providers._PROVIDER_CONFIG plus a valid model name for it.
AGENT_CONFIG = {
    "A1": {"provider": "groq", "model": "llama-3.3-70b-versatile", "side": "A"},
    "A2": {"provider": "openrouter", "model": "openai/gpt-oss-20b:free", "side": "A"},
    "B1": {"provider": "gemini", "model": "gemini-2.5-flash", "side": "B"},
    "B2": {"provider": "openai", "model": "gpt-5.4-mini", "side": "B"},
    "JUDGE": {"provider": "deepseek", "model": "deepseek-chat", "side": None},
}

# Debater 1 on each side opens and closes; debater 2 argues the middle turn.
TURN_ORDER = ["A1", "B1", "A2", "B2", "A1", "B1"]

SIDE_LABEL = {"A": "Side A", "B": "Side B"}

# Conduct rules every debater must follow, regardless of topic or model.
CONTENT_POLICY = (
    "Conduct rules, non-negotiable: Stay professional and courteous at all times. "
    "Never use unethical, racial, or discriminatory language. Base every factual "
    "claim only on publicly known, verifiable facts -- never fabricate statistics "
    "or sources. Do not use emotionally manipulative rhetoric, and never make "
    "statements designed to sway sentiment toward or against any community, group, "
    "or individual. Stay strictly relevant to the debate topic at all times."
)

# Used to pre-screen a topic before any debater or judge is invoked.
GUARDRAIL_SYSTEM = (
    "You are a content-safety gate for a debate exercise app. Decide whether the "
    "given topic is appropriate for an open, two-sided debate. REJECT any topic "
    "that would require one side to argue in favor of something illegal or "
    "clearly immoral (for example: child labor, slavery, genocide, terrorism, "
    "child exploitation, violence against a group), or that targets a protected "
    "group, or that is sexual or gratuitously violent in nature. Ordinary "
    "controversial-but-legal policy topics (for example: minimum wage, school "
    "uniforms, social media regulation, remote work) are fine and must be "
    "ALLOWED -- do not reject a topic merely for being debatable or sensitive. "
    "Respond with exactly one line: either the single word 'ALLOWED', or "
    "'REJECTED: <short reason>'."
)

# The rubric the judge must score against, in this exact order.
JUDGE_RUBRIC = (
    "Score the debate strictly on these four criteria, in this order:\n"
    "1. Rebuttal quality -- how well each side's arguments engaged with and "
    "responded to the opponent's actual points.\n"
    "2. Factual accuracy -- whether claims made are correct and verifiable, not "
    "fabricated or misleading.\n"
    "3. Relevance -- whether the facts and statements stayed on-topic rather "
    "than drifting into unrelated territory.\n"
    "4. Explain the result -- after weighing 1-3, clearly explain HOW you "
    "compared the two sides and WHY the winner was chosen over the other.\n"
    "Do not judge based on your own opinion of the topic, and do not reward "
    "rhetorical flourish over substance."
)


def trim_to_sentences(text: str, max_sentences: int = MAX_SENTENCES) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return " ".join(s for s in sentences[:max_sentences] if s).strip()
