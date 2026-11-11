#FastAPI entry point for this project
from fastapi import FastAPI

app = FastAPI(title="Malay-Japanese Adaptive Tutor", description="An adaptive tutor for  learning Malay and Japanese languages.", version="1.0.0")

@app.get("/api/health")
def heatlth():
    return {"status": "good"}