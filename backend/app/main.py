#FastAPI entry point for this project
from fastapi import FastAPI
from backend.app.config import load_settings

settings = load_settings()

app = FastAPI(title="Malay-Japanese Adaptive Tutor")

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "llm_model": settings.llm_model,
        "llm_keep_alive": settings.llm_keep_alive,
    }