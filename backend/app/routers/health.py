"""GET /api/health: is everything the tutor needs available?"""
import json
import urllib.request

from fastapi import APIRouter, Request

from backend.app import ollama_client, rag_adapter

router = APIRouter(prefix="/api")

# Health is checked often, so never wait long. (Generation uses 300 s; this uses 3.)
TIMEOUT = 3


def ollama_status(settings):
    try:
        tags = ollama_client.call(settings.llm_base_url, "tags", timeout=TIMEOUT)
    except (OSError, ValueError) as exc:
        return {"reachable": False, "error": str(exc)}
    installed = {}
    for item in tags.get("models", []):
        for name in (item.get("name"), item.get("model")):
            installed[name] = item.get("digest")
    models = {}
    for name in (settings.llm_model, rag_adapter.EMBEDDING_MODEL):
        models[name] = {"installed": name in installed, "digest": installed.get(name)}
    return {"reachable": True, "models": models}


def index_status(state):
    info = state.index_info
    if info is None:
        return {"loaded": False, "error": state.index_error}
    return {
        "loaded": True,
        "complete": info.get("complete"),
        "entries": len(state.entries),
        "dimensions": info.get("dimensions"),
        "embedding_model": info["config"]["model"],
    }


def classifier_status(settings):
    if not settings.classifier_dir.is_dir():
        return {"available": False, "reason": "No trained model folder yet (Phase 3)."}
    return {"available": False, "reason": "Classifier loading is added in Phase 3."}


def voicevox_status(settings):
    try:
        with urllib.request.urlopen(f"{settings.voicevox_url}/version", timeout=TIMEOUT) as response:
            return {"reachable": True, "version": json.load(response)}
    except (OSError, ValueError) as exc:
        return {"reachable": False, "error": str(exc)}


@router.get("/health")
def health(request: Request):
    settings = request.app.state.settings
    ollama = ollama_status(settings)
    index = index_status(request.app.state)
    ready = ollama["reachable"] and index["loaded"]
    return {
        "status": "ok" if ready else "degraded",
        "llm_model": settings.llm_model,
        "llm_keep_alive": settings.llm_keep_alive,
        "ollama": ollama,
        "index": index,
        "classifier": classifier_status(settings),
        "voicevox": voicevox_status(settings),
    }