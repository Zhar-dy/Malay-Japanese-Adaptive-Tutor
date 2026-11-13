"""Grammar retrieval endpoints."""
import time
from urllib import error

from fastapi import APIRouter, HTTPException, Request

from backend.app import rag_adapter
from backend.app.schemas import SearchRequest, SearchResponse

router = APIRouter(prefix="/api")


def retrieve(request, query, level, level_mode, top_k):
    """Filter, embed, rank. Used by /api/search now and by /api/ask in Step 4."""
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
    try:
        vector = rag_adapter.embed_question(query, state.index_info)
    except error.HTTPError as exc:
        raise HTTPException(502, f"Ollama returned HTTP {exc.code}.") from exc
    except (error.URLError, TimeoutError) as exc:
        raise HTTPException(503, "Cannot reach Ollama. Open it and retry.") from exc
    except ValueError as exc:
        raise HTTPException(502, str(exc)) from exc
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