import gradio as gr
from dotenv import load_dotenv

from debate.agents import DEFAULT_ROLE_PROVIDER, PROVIDER_DEFAULT_MODEL, build_agent_config
from debate.engine import run_debate

load_dotenv()

ROLES = ["A1", "A2", "B1", "B2", "JUDGE"]
PROVIDERS = list(PROVIDER_DEFAULT_MODEL.keys())

AGENT_TAG = {
    "A1": "🔵 A1", "A2": "🔵 A2",
    "B1": "🔴 B1", "B2": "🔴 B2",
}


def run(topic, side_a_position, side_b_position, *role_providers):
    topic = (topic or "").strip()
    if not topic:
        yield "Please enter a debate topic."
        return

    role_provider = dict(zip(ROLES, role_providers))
    debater_providers = {role_provider[r] for r in ("A1", "A2", "B1", "B2")}
    if role_provider["JUDGE"] in debater_providers:
        yield (
            "### ⚠️ Judge can't share a model with a debater\n\n"
            f"You assigned **{role_provider['JUDGE']}** to the Judge, but it's also "
            "arguing on one of the sides this run. Pick a different provider for "
            "the Judge to keep it neutral."
        )
        return

    agent_config = build_agent_config(role_provider)

    side_a_position = (side_a_position or "For").strip()
    side_b_position = (side_b_position or "Against").strip()

    assignment_line = " | ".join(f"{r}: {role_provider[r]}" for r in ROLES)
    log = (
        f"### Topic: {topic}\n**Side A:** {side_a_position}  |  **Side B:** {side_b_position}\n\n"
        f"_Model assignment — {assignment_line}_\n\n---\n\n"
    )
    yield log

    try:
        for event_type, payload in run_debate(topic, side_a_position, side_b_position, agent_config):
            if event_type == "rejected":
                log += (
                    f"### 🚫 Topic not allowed\n\n{payload['reason']}\n\n"
                    "Please choose a different, lawful and non-harmful topic."
                )
            elif event_type == "turn":
                model = agent_config[payload["agent"]]["model"]
                tag = AGENT_TAG.get(payload["agent"], payload["agent"])
                log += f"**{tag}** _(via {model})_: {payload['text']}\n\n"
            else:
                model = agent_config["JUDGE"]["model"]
                log += f"---\n\n### ⚖️ Judge's Verdict _(via {model}, uninvolved in the debate)_\n\n{payload['text']}\n"
            yield log
    except Exception as e:
        log += f"\n\n**Error:** {e}\n\nCheck that the relevant API key is set (see `.env.example`)."
        yield log


with gr.Blocks(title="AI Debate Arena") as demo:
    gr.Markdown(
        "# 🎤 AI Debate Arena\n"
        "Four AI debaters (2 per side) argue a topic you choose, then a 5th "
        "agent judges the winner. Each role's job is fixed — only *which "
        "model* plays it is up to you. Reassign providers below and rerun "
        "to see the same roles, argued by different models."
    )
    with gr.Row():
        topic_in = gr.Textbox(label="Debate topic", placeholder="e.g. Should homework be banned?", scale=2)
    with gr.Row():
        side_a_in = gr.Dropdown(choices=["For", "Against"], value="For", label="Side A position")
        side_b_in = gr.Dropdown(
            choices=["For", "Against"], value="Against", label="Side B position (auto-set to the opposite)",
            interactive=False,
        )

    with gr.Accordion("⚙️ Assign a model to each role", open=False):
        gr.Markdown(
            "Every role keeps the exact same job (opening/rebuttal instructions, "
            "conduct policy, judging rubric) no matter which provider is picked here "
            "— only the model executing that role changes."
        )
        role_dropdowns = []
        with gr.Row():
            for role in ("A1", "A2"):
                role_dropdowns.append(
                    gr.Dropdown(PROVIDERS, value=DEFAULT_ROLE_PROVIDER[role], label=f"{role} (Side A)")
                )
        with gr.Row():
            for role in ("B1", "B2"):
                role_dropdowns.append(
                    gr.Dropdown(PROVIDERS, value=DEFAULT_ROLE_PROVIDER[role], label=f"{role} (Side B)")
                )
        judge_dropdown = gr.Dropdown(PROVIDERS, value=DEFAULT_ROLE_PROVIDER["JUDGE"], label="JUDGE (neutral)")
        role_dropdowns.append(judge_dropdown)

    run_btn = gr.Button("Start Debate", variant="primary")
    output = gr.Markdown()

    def flip(side_a_position):
        return "Against" if side_a_position == "For" else "For"

    side_a_in.change(flip, inputs=side_a_in, outputs=side_b_in)
    run_btn.click(run, inputs=[topic_in, side_a_in, side_b_in, *role_dropdowns], outputs=output)

if __name__ == "__main__":
    demo.launch()
