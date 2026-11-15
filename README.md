---
title: AgenticDebate
emoji: 📊
colorFrom: yellow
colorTo: pink
sdk: gradio
sdk_version: 6.20.0
python_version: '3.13'
app_file: app.py
pinned: false
short_description: 4 low-cost models debate a user-given topic, judged by a 5th
---

# AI Debate Arena

A small exercise: give it a topic, and 4 debater agents (2 per side, each
running on a different low/no-cost model) argue it out, then a 5th agent
judges the winner.

- **A1 / A2** — Side A debaters
- **B1 / B2** — Side B debaters
- **JUDGE** — reads the full transcript and declares a winner; never argues,
  never speaks during the debate, and always runs on a model no debater uses

Turn order: `A1 -> B1 -> A2 -> B2 -> A1 -> B1 -> JUDGE`. Debater 1 on each
side opens and closes; debater 2 argues the middle turn. Every debater turn
is capped at 5 sentences and must rebut the most recent opposing point
before adding its own.

## Models

Configured in `debate/agents.py` (`AGENT_CONFIG`) — change providers/models
there:

| Agent | Provider | Model |
|-------|----------|-------|
| A1 | Groq | `openai/gpt-oss-120b` |
| A2 | OpenRouter | `openai/gpt-oss-20b:free` |
| B1 | Gemini | `gemini-2.5-flash` |
| B2 | OpenAI | `gpt-5.4-mini` |
| JUDGE | DeepSeek | `deepseek-chat` |

All five providers are called through the OpenAI-compatible chat-completions
API (`debate/providers.py`), so adding a new provider is just a new
`base_url` + API key entry.

**Judge neutrality:** the judge is intentionally on a provider/model that no
debater uses (DeepSeek, while debaters use Groq/OpenRouter/Gemini/OpenAI). If
you change `AGENT_CONFIG`, keep that non-overlap — a judge sharing a model
with one of the debaters isn't neutral.

## Guardrails

- **Topic screening** (`check_topic_allowed` in `debate/engine.py`): before
  any debater or judge runs, the topic is checked by a fast model against
  `GUARDRAIL_SYSTEM` in `debate/agents.py`. Topics that would require arguing
  in favor of something illegal or clearly immoral (e.g. child labor,
  slavery, genocide, terrorism) are rejected outright — ordinary
  controversial-but-legal topics (minimum wage, school uniforms, etc.) are
  allowed. A rejected topic never reaches the debaters.
- **Debater conduct** (`CONTENT_POLICY` in `debate/agents.py`, injected into
  every debater's system prompt): professional and courteous tone only, no
  unethical/racial/discriminatory language, claims must be based on publicly
  verifiable facts (no fabricated statistics), no emotionally manipulative
  rhetoric or statements aimed at swaying sentiment toward/against any
  community or group, and strict relevance to the topic.
- **Judging rubric** (`JUDGE_RUBRIC` in `debate/agents.py`): the judge scores
  in this fixed order — (1) rebuttal quality against the opponent's actual
  points, (2) factual accuracy, (3) topical relevance, then (4) an explicit
  explanation of how and why the winner was chosen.

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
- OpenRouter free models: `curl -s https://openrouter.ai/api/v1/models | jq -r '.data[] | select(.id | endswith(":free")) | .id'`
  — the free-tier lineup changes often (a Llama free slug used here previously
  got retired mid-project), so re-run that check rather than trusting a
  hardcoded slug. Currently uses `openai/gpt-oss-20b:free` for A2.
- DeepSeek: https://platform.deepseek.com/api_keys (if you'd rather not hold
  a separate DeepSeek key, point `JUDGE` in `AGENT_CONFIG` at whatever
  DeepSeek-family `:free` slug OpenRouter currently lists, `"provider":
  "openrouter"` — just make sure it stays distinct from whichever debater is
  already on OpenRouter, and check the live list above first since availability
  varies)

## Deploying to Hugging Face Spaces

1. Create a new Space, SDK = **Gradio**.
2. Push this repo to the Space's git remote (the `README.md` frontmatter
   above already declares `app_file: app.py`, so no extra config needed).
3. In the Space's **Settings -> Repository secrets**, add whichever of
   `GROQ_API_KEY` / `GEMINI_API_KEY` / `OPENROUTER_API_KEY` / `OPENAI_API_KEY` /
   `DEEPSEEK_API_KEY` your `AGENT_CONFIG` uses — these become environment
   variables at runtime, same as `.env` locally.
