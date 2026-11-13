"""FastAPI entry point for the Malay-Japanese Adaptive Tutor."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from backend.app import rag_adapter
from backend.app.services import store
from backend.app.config import load_settings
from backend.app.routers import rag

settings = load_settings()


@asynccontextmanager
async def lifespan(app):
    # Runs ONCE when the server starts, before the first request.
    app.state.settings = settings
    store.init_db(settings.app_db_path)
    try:
        app.state.index_info, app.state.entries = rag_adapter.load_index(settings.index_path)
        app.state.index_error = None
    except Exception as exc:
        # Keep the server running so /api/health can explain what is wrong.
        app.state.index_info, app.state.entries = None, []
        app.state.index_error = str(exc)
    yield
    # Code after `yield` runs once when the server stops (nothing to clean up yet).


app = FastAPI(
    title="Malay-Japanese Adaptive Tutor",
    description="Japanese tutor for Malaysian learners using RAG and scaffolding",
    version="0.1.0",
    lifespan=lifespan,
)
app.include_router(rag.router)


@app.get("/api/health")
def health(request: Request):
    return {
        "status": "ok",
        "llm_model": settings.llm_model,
        "llm_keep_alive": settings.llm_keep_alive,
        "index": {
            "loaded": request.app.state.index_info is not None,
            "entries": len(request.app.state.entries),
            "error": request.app.state.index_error,
        },
    }