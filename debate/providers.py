import os

from openai import OpenAI

# All four providers speak the OpenAI chat-completions wire format, so a
# single client class works for everyone -- only base_url/api_key differ.
_PROVIDER_CONFIG = {
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "api_key_env": "GROQ_API_KEY",
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "api_key_env": "GEMINI_API_KEY",
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
    },
    "openai": {
        "base_url": None,
        "api_key_env": "OPENAI_API_KEY",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "api_key_env": "DEEPSEEK_API_KEY",
    },
}

_clients = {}


def _get_client(provider: str) -> OpenAI:
    if provider not in _clients:
        cfg = _PROVIDER_CONFIG[provider]
        api_key = os.environ.get(cfg["api_key_env"])
        if not api_key:
            raise RuntimeError(
                f"Missing {cfg['api_key_env']} in the environment for provider '{provider}'."
            )
        kwargs = {"api_key": api_key}
        if cfg["base_url"]:
            kwargs["base_url"] = cfg["base_url"]
        _clients[provider] = OpenAI(**kwargs)
    return _clients[provider]


def call_llm(
    provider: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.8,
) -> str:
    client = _get_client(provider)
    try:
        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
    except Exception as e:
        cfg = _PROVIDER_CONFIG[provider]
        raise RuntimeError(
            f"[provider={provider} model={model} env_var={cfg['api_key_env']}] {e}"
        ) from e
    return (response.choices[0].message.content or "").strip()
