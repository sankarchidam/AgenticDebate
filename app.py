import gradio as gr
from dotenv import load_dotenv

from debate.agents import AGENT_CONFIG
from debate.engine import run_debate

load_dotenv()

AGENT_TAG = {
    "A1": "🔵 A1", "A2": "🔵 A2",
    "B1": "🔴 B1", "B2": "🔴 B2",
}


def run(topic, side_a_position, side_b_position):
    topic = (topic or "").strip()
    if not topic:
        yield "Please enter a debate topic."
        return

    side_a_position = (side_a_position or "For").strip()
    side_b_position = (side_b_position or "Against").strip()

    log = f"### Topic: {topic}\n**Side A:** {side_a_position}  |  **Side B:** {side_b_position}\n\n---\n\n"
    yield log

    try:
        for event_type, payload in run_debate(topic, side_a_position, side_b_position):
            if event_type == "turn":
                model = AGENT_CONFIG[payload["agent"]]["model"]
                tag = AGENT_TAG.get(payload["agent"], payload["agent"])
                log += f"**{tag}** _(via {model})_: {payload['text']}\n\n"
            else:
                log += f"---\n\n### 🏛️ Judge's Verdict\n\n{payload['text']}\n"
            yield log
    except RuntimeError as e:
        log += f"\n\n**Error:** {e}\n\nCheck that the relevant API key is set (see `.env.example`)."
        yield log


with gr.Blocks(title="AI Debate Arena") as demo:
    gr.Markdown(
        "# 🎤 AI Debate Arena\n"
        "Four AI debaters (2 per side, each a different low/no-cost model) argue "
        "a topic you choose, then an AI judge decides the winner."
    )
    with gr.Row():
        topic_in = gr.Textbox(label="Debate topic", placeholder="e.g. Should homework be banned?", scale=2)
    with gr.Row():
        side_a_in = gr.Textbox(label="Side A position", value="For")
        side_b_in = gr.Textbox(label="Side B position", value="Against")
    run_btn = gr.Button("Start Debate", variant="primary")
    output = gr.Markdown()

    run_btn.click(run, inputs=[topic_in, side_a_in, side_b_in], outputs=output)

if __name__ == "__main__":
    demo.launch()
