#FastAPI entry point for this project
from fastapi import FastAPI
from backend.app.config import load_settings

settings = load_settings()

app = FastAPI(title="Malay-Japanese Adaptive Tutor", description="An adaptive tutor for  learning Malay and Japanese languages.", version="1.0.0")

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "llm_model": settings.llm_model,
        "llm_keep_alive": settings.llm_keep_alive,
    }