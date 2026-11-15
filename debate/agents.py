import re

MAX_SENTENCES = 5

# --- Roles vs. models -------------------------------------------------------
# A "role" (A1/A2/B1/B2/JUDGE) is a fixed job: which side it argues (or none,
# for the judge), and where it sits in TURN_ORDER. That never changes.
# A "model" is just which provider executes that role -- purely swappable,
# which is the whole point of this project (see build_agent_config below).

ROLE_SIDE = {"A1": "A", "A2": "A", "B1": "B", "B2": "B", "JUDGE": None}

# One representative free/cheap model per provider. Swap these, or add new
# providers to providers._PROVIDER_CONFIG, without touching any role logic
# in engine.py -- roles and responsibilities are defined once, independent
# of which model plays them.
PROVIDER_DEFAULT_MODEL = {
    "groq": "openai/gpt-oss-120b",
    "gemini": "gemini-2.5-flash",
    "openrouter": "nvidia/nemotron-3-ultra-550b-a55b:free",
    "openai": "gpt-5.4-mini",
    "deepseek": "deepseek-chat",
}

# Which provider plays which role by default. JUDGE deliberately gets a
# provider no debater uses -- a judge that shares a model with one of the
# debaters is not neutral. The Gradio UI lets this be reassigned per run;
# build_agent_config() is how a role -> provider mapping becomes the full
# role -> {provider, model, side} config run_debate() actually uses.
DEFAULT_ROLE_PROVIDER = {
    "A1": "groq",
    "A2": "openrouter",
    "B1": "gemini",
    "B2": "openai",
    "JUDGE": "deepseek",
}


def build_agent_config(role_provider: dict) -> dict:
    """Turn a {role: provider} mapping into the full {role: {provider, model,
    side}} config run_debate() needs. This is the single seam where "who
    plays this role" gets decided -- everything else (prompts, turn order,
    conduct policy, judging rubric) is provider-agnostic."""
    return {
        role: {
            "provider": provider,
            "model": PROVIDER_DEFAULT_MODEL[provider],
            "side": ROLE_SIDE[role],
        }
        for role, provider in role_provider.items()
    }


# Default config, used whenever a caller doesn't supply its own role->provider
# mapping (e.g. check_keys.py, or run_debate() with no override).
AGENT_CONFIG = build_agent_config(DEFAULT_ROLE_PROVIDER)

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
