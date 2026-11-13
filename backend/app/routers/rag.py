"""Grammar retrieval and explanation endpoints."""
from contextlib import contextmanager
import time
from urllib import error

from fastapi import APIRouter, HTTPException, Request

from backend.app import rag_adapter
from backend.app.schemas import AskRequest, AskResponse, SearchRequest, SearchResponse
from backend.app.services import tutor

router = APIRouter(prefix="/api")


@contextmanager
def ollama_errors():
    """Turn Ollama failures into clear HTTP errors for the browser."""
    try:
        yield
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise HTTPException(502, f"Ollama returned HTTP {exc.code}: {detail}") from exc
    except (error.URLError, TimeoutError) as exc:
        raise HTTPException(503, "Cannot reach Ollama. Open it and retry.") from exc
    except ValueError as exc:
        raise HTTPException(502, str(exc)) from exc


def retrieve(request, query, level, level_mode, top_k):
    """Filter, embed, rank. Shared by /api/search and /api/ask."""
    state = request.app.state
    if state.index_info is None:
        raise HTTPException(503, f"Grammar index not loaded: {state.index_error}")
    if not query.strip():
        raise HTTPException(422, "Query must not be empty.")

    levels = rag_adapter.allowed_levels(level, level_mode)
    entries = rag_adapter.filter_entries(state.entries, levels)
    if not entries:
        raise HTTPException(404, "No grammar entries match the level filter.")

    start = time.perf_counter()
    with ollama_errors():
        vector = rag_adapter.embed_question(query, state.index_info)
    embedded = time.perf_counter()

    hits = rag_adapter.rank_entries(vector, entries, top_k)
    ranked = time.perf_counter()

    timing = {
        "embed": round((embedded - start) * 1000),
        "rank": round((ranked - embedded) * 1000),
    }
    return levels, hits, timing


@router.post("/search", response_model=SearchResponse)
def search(body: SearchRequest, request: Request):
    levels, hits, timing = retrieve(
        request, body.query, body.level, body.level_mode, body.top_k)
    return {
        "query": body.query,
        "level_filter": levels,
        "embedding_model": rag_adapter.EMBEDDING_MODEL,
        "hits": [rag_adapter.format_hit(n, hit) for n, hit in enumerate(hits, start=1)],
        "timing_ms": timing,
    }


@router.post("/ask", response_model=AskResponse)
def ask(body: AskRequest, request: Request):
    levels, hits, timing = retrieve(
        request, body.question, body.level, body.level_mode, body.top_k)
    sources = [rag_adapter.format_hit(n, hit) for n, hit in enumerate(hits, start=1)]

    with ollama_errors():
        result = tutor.explain(request.app.state.settings, body.question, sources,
                               think=body.think, explain_lang=body.explain_lang)

    timing["generate"] = result["generate_ms"]
    return {
        "answer": result["answer"],
        "sources": sources,
        "warnings": result["warnings"],
        "truncated": result["truncated"],
        "model": result["model"],
        "model_digest": result["model_digest"],
        "timing_ms": timing,
        "eval_count": result["eval_count"],
    }