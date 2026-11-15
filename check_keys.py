"""Ping each configured provider with a trivial request and report which
API keys are valid. Run locally with your .env loaded:

    python check_keys.py

Never prints key values -- only PASS/FAIL per provider.
"""

from dotenv import load_dotenv

from debate.providers import _PROVIDER_CONFIG, call_llm

load_dotenv()

# One cheap/fast model per provider, just to confirm the key + endpoint work.
PROBE_MODEL = {
    "groq": "openai/gpt-oss-120b",
    "gemini": "gemini-2.5-flash",
    "openrouter": "openai/gpt-oss-20b:free",
    "openai": "gpt-5.4-mini",
    "deepseek": "deepseek-chat",
}


def main():
    for provider, cfg in _PROVIDER_CONFIG.items():
        model = PROBE_MODEL.get(provider)
        try:
            call_llm(provider, model, "Reply with just: OK", "ping", temperature=0.0)
        except RuntimeError as e:
            msg = str(e)
            if "Missing" in msg:
                print(f"SKIP  {provider:10} ({cfg['api_key_env']} not set)")
            else:
                print(f"FAIL  {provider:10} ({cfg['api_key_env']}) -> {msg}")
            continue
        print(f"PASS  {provider:10} ({cfg['api_key_env']})")


if __name__ == "__main__":
    main()
