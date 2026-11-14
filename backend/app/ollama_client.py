"""Small client for Ollama's chat API.

Follows 4 rules for talking to Ollama:
1. /api/chat only   2. "think" at the top level   3. only sampling values in "options"
4. every reply goes through parse_ollama_tutor_response() first.
"""
import json
from urllib import request

from backend.app import rag_adapter


def call(base_url, endpoint, payload=None, timeout=300):
    """Send one request to Ollama and return its JSON reply as a dict."""
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(f"{base_url}/api/{endpoint}", data=body,
                          headers={"Content-Type": "application/json"})
    with request.urlopen(req, timeout=timeout) as response:
        result = json.load(response)
    if result.get("error"):
        raise ValueError(f"Ollama error: {result['error']}")
    return result


def model_digest(base_url, model):
    """Return the digest (exact version ID) of an installed model."""
    for item in call(base_url, "tags").get("models", []):
        if model in (item.get("name"), item.get("model")):
            return item.get("digest")
    raise ValueError(f"Model {model} is not installed. Run: ollama pull {model}")


def chat(base_url, model, messages, keep_alive, think=False, options=None, format_schema=None):
    """Ask the model to reply to `messages`. Returns the parsed reply as a dict."""
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,            # rule 3: top level. One full reply, not word by word
        "think": think,             # rule 2: top level, NEVER inside "options"
        "keep_alive": keep_alive,   # rule 3: top level
        "options": options or {},   # rule 3: only sampling values go in here
    }
    if format_schema is not None:
        payload["format"] = format_schema  # rule 3: top level (JSON output, used in Phase 2)

    result = call(base_url, "chat", payload)                   # rule 1: /api/chat only
    parsed = rag_adapter.parse_ollama_tutor_response(result)   # rule 4: always first
    parsed["model"] = result.get("model", model)
    parsed["raw_output"] = (result.get("message") or {}).get("content", "")  # kept for logging (Step 5)
    return parsed