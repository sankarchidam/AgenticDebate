from .agents import (
    AGENT_CONFIG,
    CONTENT_POLICY,
    GUARDRAIL_SYSTEM,
    JUDGE_RUBRIC,
    SIDE_LABEL,
    TURN_ORDER,
    trim_to_sentences,
)
from .providers import call_llm

# Fast/cheap model used only to screen the topic itself -- not a debate
# participant, so reusing a debater's provider here is fine.
GUARDRAIL_PROVIDER = "groq"
GUARDRAIL_MODEL = "llama-3.3-70b-versatile"


def format_transcript(transcript):
    if not transcript:
        return "(No arguments yet — you are opening the debate.)"
    return "\n".join(
        f"[{SIDE_LABEL[t['side']]} - {t['agent']}]: {t['text']}" for t in transcript
    )


def check_topic_allowed(topic: str) -> tuple[bool, str]:
    """Screen a topic before any debater or judge is invoked. Returns
    (allowed, reason) -- reason is only populated when rejected."""
    verdict = call_llm(
        GUARDRAIL_PROVIDER,
        GUARDRAIL_MODEL,
        GUARDRAIL_SYSTEM,
        f'Topic: "{topic}"',
        temperature=0.0,
    ).strip()

    if verdict.upper().startswith("ALLOWED"):
        return True, ""

    reason = verdict.split(":", 1)[1].strip() if ":" in verdict else verdict
    return False, reason or "This topic is not appropriate for debate (immoral or illegal)."


def run_debate(topic: str, side_a_position: str, side_b_position: str):
    """Generator yielding ('rejected', {...}) and stopping if the topic fails
    the guardrail check; otherwise ('turn', {...}) for each debater turn,
    then ('verdict', {...}) once at the end."""
    allowed, reason = check_topic_allowed(topic)
    if not allowed:
        yield ("rejected", {"reason": reason})
        return

    transcript = []
    positions = {"A": side_a_position, "B": side_b_position}

    for agent_id in TURN_ORDER:
        cfg = AGENT_CONFIG[agent_id]
        side = cfg["side"]
        is_opening = not any(t["agent"] == agent_id for t in transcript)
        history = format_transcript(transcript)

        instruction = (
            "Open with your strongest point."
            if is_opening
            else (
                "Directly rebut the most recent opposing argument, then add or "
                "extend your side's case. Do not repeat points your teammate "
                "already made."
            )
        )
        system_prompt = (
            f"You are debater {agent_id}, arguing the '{positions[side]}' position "
            f'on the topic: "{topic}". Respond in no more than 5 sentences. '
            f"Be persuasive and specific. {instruction} {CONTENT_POLICY}"
        )
        user_prompt = f"Debate so far:\n{history}\n\nYour turn ({agent_id}, {SIDE_LABEL[side]}):"

        text = call_llm(cfg["provider"], cfg["model"], system_prompt, user_prompt)
        text = trim_to_sentences(text)

        turn = {"agent": agent_id, "side": side, "text": text}
        transcript.append(turn)
        yield ("turn", turn)

    judge_cfg = AGENT_CONFIG["JUDGE"]
    judge_system = (
        f'You are an impartial debate judge evaluating a debate on: "{topic}". '
        f"Side A argued: '{side_a_position}'. Side B argued: '{side_b_position}'. "
        "You did not participate in the debate and have no stake in either side. "
        f"{JUDGE_RUBRIC} End with exactly one line, verbatim: 'WINNER: Side A' "
        "or 'WINNER: Side B'."
    )
    judge_prompt = f"Full transcript:\n{format_transcript(transcript)}\n\nYour verdict:"
    verdict = call_llm(
        judge_cfg["provider"], judge_cfg["model"], judge_system, judge_prompt, temperature=0.3
    )

    yield ("verdict", {"agent": "JUDGE", "text": verdict})
