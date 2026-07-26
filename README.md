---
title: AI Debate Arena
emoji: 🎤
colorFrom: blue
colorTo: red
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
---

# AI Debate Arena

A small exercise: give it a topic, and 4 debater agents (2 per side, each
running on a different low/no-cost model) argue it out, then a 5th agent
judges the winner.

- **A1 / A2** — Side A debaters
- **B1 / B2** — Side B debaters
- **JUDGE** — reads the full transcript and declares a winner

Turn order: `A1 -> B1 -> A2 -> B2 -> A1 -> B1 -> JUDGE`. Debater 1 on each
side opens and closes; debater 2 argues the middle turn. Every debater turn
is capped at 5 sentences and must rebut the most recent opposing point
before adding its own.

## Models

Configured in `debate/agents.py` (`AGENT_CONFIG`) — change providers/models
there:

| Agent | Provider | Model |
|-------|----------|-------|
| A1 | Groq | `llama-3.3-70b-versatile` |
| A2 | OpenRouter | `meta-llama/llama-3.1-8b-instruct:free` |
| B1 | Gemini | `gemini-2.5-flash` |
| B2 | OpenAI | `gpt-5.4-mini` |
| JUDGE | Gemini | `gemini-2.5-flash` |

All four providers are called through the OpenAI-compatible chat-completions
API (`debate/providers.py`), so adding a new provider is just a new
`base_url` + API key entry.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in whichever API keys you actually use
python app.py
```

You only need an API key for the providers referenced in `AGENT_CONFIG` —
if you're not using OpenRouter, for example, you can leave
`OPENROUTER_API_KEY` blank.

- Groq free tier: https://console.groq.com
- Gemini free tier: https://aistudio.google.com/apikey
- OpenRouter free models: https://openrouter.ai/models?max_price=0

## Deploying to Hugging Face Spaces

1. Create a new Space, SDK = **Gradio**.
2. Push this repo to the Space's git remote (the `README.md` frontmatter
   above already declares `app_file: app.py`, so no extra config needed).
3. In the Space's **Settings -> Repository secrets**, add whichever of
   `GROQ_API_KEY` / `GEMINI_API_KEY` / `OPENROUTER_API_KEY` / `OPENAI_API_KEY`
   your `AGENT_CONFIG` uses — these become environment variables at runtime,
   same as `.env` locally.
