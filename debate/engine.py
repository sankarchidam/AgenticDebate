from .agents import AGENT_CONFIG, SIDE_LABEL, TURN_ORDER, trim_to_sentences
from .providers import call_llm


def format_transcript(transcript):
    if not transcript:
        return "(No arguments yet — you are opening the debate.)"
    return "\n".join(
        f"[{SIDE_LABEL[t['side']]} - {t['agent']}]: {t['text']}" for t in transcript
    )


def run_debate(topic: str, side_a_position: str, side_b_position: str):
    """Generator yielding ('turn', {...}) for each debater turn, then
    ('verdict', {...}) once at the end."""
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
            f"Be persuasive and specific. {instruction}"
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
        f"Side A argues: '{side_a_position}'. Side B argues: '{side_b_position}'. "
        "Judge only on argument quality, rebuttal strength, and persuasiveness "
        "— not your personal opinion on the topic. Give a short verdict (max 6 "
        "sentences), then end with exactly one line, verbatim: 'WINNER: Side A' "
        "or 'WINNER: Side B'."
    )
    judge_prompt = f"Full transcript:\n{format_transcript(transcript)}\n\nYour verdict:"
    verdict = call_llm(
        judge_cfg["provider"], judge_cfg["model"], judge_system, judge_prompt, temperature=0.3
    )

    yield ("verdict", {"agent": "JUDGE", "text": verdict})
