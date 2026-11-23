"""Grammar retrieval and explanation endpoints."""
from fastapi import APIRouter, Request

from backend.app import rag_adapter
from backend.app.schemas import AskRequest, AskResponse, SearchRequest, SearchResponse
from backend.app.services import store, tutor
from backend.app.services.retrieval import ollama_errors, retrieve

router = APIRouter(prefix="/api")

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
    timing["llm_load"] = result["ollama_ms"]["load"]
    timing["llm_prompt_eval"] = result["ollama_ms"]["prompt_eval"]
    timing["llm_eval"] = result["ollama_ms"]["eval"]
    settings = request.app.state.settings
    item_id = store.log_ask(
        settings.app_db_path,
        question=body.question, level=body.level, explain_lang=body.explain_lang,
        sources=sources,
        retrieval={"query": body.question, "level_filter": levels,
                   "level_mode": body.level_mode, "top_k": body.top_k},
        result=result, timing=timing)
    return {
        "answer": result["answer"],
        "sources": sources,
        "warnings": result["warnings"],
        "truncated": result["truncated"],
        "model": result["model"],
        "model_digest": result["model_digest"],
        "timing_ms": timing,
        "eval_count": result["eval_count"],
        "prompt_eval_count": result["prompt_eval_count"],
        "item_id": item_id,
    }