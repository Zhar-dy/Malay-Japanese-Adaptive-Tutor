# settings for this web app, read from env variable or .env file

from dataclasses import dataclass
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def read_env_file(path):
    # read key=value lines from .env file. Blank lines and # comments are ignored.
    values = {}
    if not path.is_file():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values

@dataclass(frozen=True)
class Settings:
    index_path: Path
    llm_model: str
    llm_base_url: str
    llm_keep_alive: str
    eval_seed: int
    classifier_dir: Path
    voicevox_url: str
    voicevox_speaker: int
    app_db_path: Path


def load_settings(env_file=ROOT / ".env"):
    file_values = read_env_file(env_file)

    def get(key, default):
        # A real environment variable wins over the .env file.
        return os.environ.get(key, file_values.get(key, default))

    def path(key, default):
        value = Path(get(key, default))
        return value if value.is_absolute() else ROOT / value

    return Settings(
        index_path=path("INDEX_PATH", "data/indexes/grammar.sqlite3"),
        llm_model=get("LLM_MODEL", "qwen3.5:4b"),
        llm_base_url=get("LLM_BASE_URL", "http://127.0.0.1:11434").rstrip("/"),
        llm_keep_alive=get("LLM_KEEP_ALIVE", "10m"),
        eval_seed=int(get("EVAL_SEED", "259")),
        classifier_dir=path("CLASSIFIER_DIR", "models/jlpt-bert"),
        voicevox_url=get("VOICEVOX_URL", "http://127.0.0.1:50021").rstrip("/"),
        voicevox_speaker=int(get("VOICEVOX_SPEAKER", "1")),
        app_db_path=path("APP_DB_PATH", "data/app/tutor.sqlite3"),
    )