"""Calls the language model for /api/ask (Phase 2 adds hints here)."""
import threading
import time

from backend.app import ollama_client, prompts, rag_adapter

# Same sampling values as scripts/rag/ask_grammar_tutor.py.
# Careful: this "top_k" is the MODEL's word choice (20 candidate words),
# NOT the number of grammar sources.
ASK_OPTIONS = {"temperature": 0.2, "top_p": 0.85, "top_k": 20, "num_ctx": 4096}

# One generation at a time: our 4 GB GTX GPU cannot run two at once.
GENERATION_LOCK = threading.Lock()


def explain(settings, question, sources, think=False, explain_lang="ms"):
    if not sources:
        raise ValueError("No retrieved sources; generation was not started.")
    options = dict(ASK_OPTIONS, num_predict=1536 if think else 512)
    messages = prompts.ask_messages(question, sources, explain_lang)

    with GENERATION_LOCK:
        digest = ollama_client.model_digest(settings.llm_base_url, settings.llm_model)
        start = time.perf_counter()
        result = ollama_client.chat(
            settings.llm_base_url, settings.llm_model, messages,
            keep_alive=settings.llm_keep_alive, think=think, options=options)
        result["generate_ms"] = round((time.perf_counter() - start) * 1000)

    if not result["answer"] and not result["truncated"]:
        raise ValueError("The model returned no answer.")
    result["model_digest"] = digest
    result["warnings"] = rag_adapter.citation_warnings(result["answer"], len(sources))
    if result["truncated"]:
        result["warnings"].append("Generation reached its token limit and may be incomplete.")
    result["messages"] = messages
    
    return result