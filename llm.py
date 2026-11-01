"""LLM backend, same setup as the Myweb repo (lib/ai/config.ts, app/api/chat, lib/rag/ollama.ts):

1. Claude via the Anthropic SDK when ANTHROPIC_API_KEY or ANTHROPIC_AUTH_TOKEN is set
   (CHAT_MODEL, default claude-haiku-5-5, effort low).
2. Otherwise the local Ollama server (OLLAMA_URL, ANALYZE_MODEL default qwen2.5:7b) in JSON mode.
3. Otherwise None, so callers fall back to their template engine. Any failure also returns None.
"""
from __future__ import annotations

import json
import os
import time
import urllib.request


def chat_model() -> str:
    return os.getenv("CHAT_MODEL") or "claude-haiku-5-5"


def ollama_url() -> str:
    return (os.getenv("OLLAMA_URL") or "http://127.0.0.1:11434").rstrip("/")


def analyze_model() -> str:
    return os.getenv("ANALYZE_MODEL") or "qwen2.5:7b"


def claude_enabled() -> bool:
    return bool(os.getenv("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_AUTH_TOKEN"))


_ready_cache: dict[tuple[str, str], tuple[float, bool]] = {}


def ollama_ready() -> bool:
    """True when Ollama answers and has ANALYZE_MODEL pulled. Cached for 60 s per url/model."""
    key = (ollama_url(), analyze_model())
    hit = _ready_cache.get(key)
    if hit and time.monotonic() - hit[0] < 60:
        return hit[1]
    try:
        with urllib.request.urlopen(f"{key[0]}/api/tags", timeout=3) as res:
            names = [m["name"] for m in json.load(res).get("models", [])]
        ready = any(n == key[1] or n.startswith(f"{key[1]}:") for n in names)
    except (OSError, ValueError, KeyError):
        ready = False
    _ready_cache[key] = (time.monotonic(), ready)
    return ready


def backend_label() -> str:
    if claude_enabled():
        return f"Claude · {chat_model()}"
    if ollama_ready():
        return f"Ollama · {analyze_model()} (local)"
    return "Offline template engine (start Ollama or set ANTHROPIC_API_KEY)"


def _parse(raw: str) -> dict | None:
    try:
        return json.loads(raw[raw.index("{"): raw.rindex("}") + 1])
    except ValueError:
        return None


def _claude(system: str, prompt: str, max_tokens: int) -> dict | None:
    try:
        import anthropic
    except ImportError:
        return None
    try:
        response = anthropic.Anthropic().messages.create(
            model=chat_model(),
            max_tokens=max_tokens,
            output_config={"effort": "low"},
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
    except anthropic.AuthenticationError:
        print("[llm] Anthropic authentication failed - check ANTHROPIC_API_KEY")
        return None
    except anthropic.RateLimitError:
        print("[llm] Anthropic rate limit")
        return None
    except anthropic.APIError as err:
        print(f"[llm] Anthropic API error: {err}")
        return None
    if response.stop_reason == "refusal":
        return None
    return _parse("".join(block.text for block in response.content if block.type == "text"))


def _ollama(system: str, prompt: str) -> dict | None:
    body = json.dumps({
        "model": analyze_model(), "stream": False, "format": "json",
        "options": {"num_ctx": 16384, "temperature": 0.2},
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
    }).encode()
    req = urllib.request.Request(f"{ollama_url()}/api/chat", data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as res:
            return _parse(json.load(res)["message"]["content"])
    except (OSError, ValueError, KeyError) as err:
        print(f"[llm] Ollama unavailable: {err}")
        return None


_last_source = "templates"


def ask_json(prompt: str, system: str = "Reply with only a JSON object.", max_tokens: int = 2048) -> dict | None:
    """One JSON completion from the best available backend, or None. See last_source()."""
    global _last_source
    if claude_enabled():
        result = _claude(system, prompt, max_tokens)
        if result is not None:
            _last_source = f"claude:{chat_model()}"
            return result
    result = _ollama(system, prompt) if ollama_ready() else None
    _last_source = f"ollama:{analyze_model()}" if result is not None else "templates"
    return result


def last_source() -> str:
    """Which backend produced the last ask_json result: claude:<model>, ollama:<model> or templates."""
    return _last_source
