# Running the Web App (Phase 1)

How to start the local web tutor. For building the grammar index and the command-line
scripts, see [RAG_SETUP.md](RAG_SETUP.md).

## 1. One-time setup

Requirements: Windows 10/11, Python 3.10+, [Ollama](https://ollama.com), and the grammar
index already built (`data/indexes/grammar.sqlite3`, see RAG_SETUP.md).

```powershell
# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install the web dependencies
pip install -r requirements-web.txt

# Download the two models
ollama pull embeddinggemma:300m
ollama pull qwen3.5:4b

# Create your settings file (every setting is optional)
Copy-Item .env.example .env
```

## 2. Start the app

1. Make sure Ollama is running (llama icon in the Windows tray, or `ollama list` works).
2. Start the server from the project folder:

```powershell
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

3. Open the pages:

| URL | What it is |
| --- | --- |
| http://127.0.0.1:8000/ | Ask page (Tanya tatabahasa) |
| http://127.0.0.1:8000/docs | Interactive API documentation |
| http://127.0.0.1:8000/api/health | Status of Ollama, the index, the classifier and VOICEVOX |

Stop the server with `Ctrl + C`. Add `--reload` while developing so the server restarts
when a `.py` file changes. Changes to `.env` need a manual restart.

## 3. Settings (`.env`)

| Setting | Default | Meaning |
| --- | --- | --- |
| `LLM_MODEL` | `qwen3.5:4b` | Ollama model used for answers |
| `LLM_KEEP_ALIVE` | `10m` | How long the model stays loaded after an answer. `0` unloads it every time, like the CLI |
| `INDEX_PATH` | `data/indexes/grammar.sqlite3` | Grammar index |
| `APP_DB_PATH` | `data/app/tutor.sqlite3` | Log of every answer (git-ignored) |

See `.env.example` for all settings.

## 4. Run the tests

The API tests fake Ollama and the index, so they need neither:

```powershell
.venv\Scripts\python.exe -m unittest tests/test_api.py -v
.venv\Scripts\python.exe -m unittest tests/test_rag.py -v
```

`test_rag.py` uses the real local index.

## 5. Troubleshooting

| Problem | Likely cause and fix |
| --- | --- |
| `503 Cannot reach Ollama` | Ollama is not running. Open it and retry |
| `502 Ollama returned HTTP 500` | Often a request sent while the model was still loading or unloading. Wait a few seconds and retry once |
| `/api/health` shows `"status": "degraded"` | Read the `ollama` and `index` parts of the response |
| First answer is slow (30–60 s) | The model is loading into memory. See `LLM_KEEP_ALIVE` |
| `ImportError` on start | Check file names and that you started from the project folder |