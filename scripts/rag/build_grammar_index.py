"""Step 4: save main grammar embeddings in a resumable local SQLite index."""
import argparse
from contextlib import closing
import hashlib
import json
import math
from pathlib import Path
import sqlite3
import sys
from urllib import error, request

MODEL = "embeddinggemma:300m"
BASE_URL = "http://localhost:11434/api/"


def json_text(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def load_grammar(file_path):
    rows = []
    ids = set()
    with file_path.open(encoding="utf-8-sig") as source:
        for line_number, line in enumerate(source, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
                if row["metadata"]["chunk_type"] != "grammar":
                    continue
                if not row["id"] or not row["text"] or row["id"] in ids:
                    raise ValueError("Missing text/ID or duplicate ID")
                expected_hash = row["metadata"]["content_sha256"]
                if hashlib.sha256(row["text"].encode("utf-8")).hexdigest() != expected_hash:
                    raise ValueError("Content hash mismatch")
            except (ValueError, KeyError, TypeError) as exc:
                raise ValueError(f"Check source line {line_number}: {exc}") from exc
            ids.add(row["id"])
            rows.append(row)
    if not rows:
        raise ValueError("No main grammar entries found.")
    return rows


def ollama_api(endpoint, payload=None):
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    req = request.Request(BASE_URL + endpoint, data=body,
                          headers={"Content-Type": "application/json"})
    with request.urlopen(req, timeout=300) as response:
        result = json.load(response)
    if result.get("error"):
        raise ValueError(str(result["error"]))
    return result


def model_digest():
    for item in ollama_api("tags").get("models", []):
        if MODEL in (item.get("name"), item.get("model")):
            return item["digest"]
    raise ValueError(f"Model missing. Run: ollama pull {MODEL}")


def embed_batch(rows):
    inputs = [
        f"title: {row['metadata'].get('pattern', 'none')} | text: {row['text']}"
        for row in rows
    ]
    vectors = ollama_api("embed", {
        "model": MODEL, "input": inputs, "truncate": False, "keep_alive": "5m",
    })["embeddings"]
    if len(vectors) != len(rows):
        raise ValueError("Ollama returned an unexpected number of embeddings.")
    for vector in vectors:
        if not vector or not all(
            isinstance(x, (int, float)) and math.isfinite(x) for x in vector):
            raise ValueError("Invalid embedding values.")
        if math.sqrt(sum(x * x for x in vector)) == 0:
            raise ValueError("Cannot store a zero vector.")
    return vectors


def set_metadata(db, key, value):
    db.execute("INSERT OR REPLACE INTO metadata VALUES (?, ?)", (key, json_text(value)))


def build_index(rows, index_path, batch_size=16):
    if batch_size < 1:
        raise ValueError("Batch size must be positive.")
    config = {
        "format": "embeddinggemma-retrieval-v1",
        "model": MODEL,
        "model_digest": model_digest(),
        "data_sha256": hashlib.sha256(json_text(rows).encode("utf-8")).hexdigest(),
        "expected_count": len(rows),
        "selection": "main grammar entries only",
    }
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(index_path)) as db:
        db.execute("CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT)")
        db.execute("""CREATE TABLE IF NOT EXISTS chunks (
            id TEXT PRIMARY KEY, text TEXT, metadata_json TEXT, embedding_json TEXT)""")
        saved = {key: json.loads(value)
                 for key, value in db.execute("SELECT key, value FROM metadata")}
        if saved and saved.get("config") != config:
            raise ValueError("Data or embedding model changed. Use a NEW --index path.")
        if not saved:
            with db:
                set_metadata(db, "config", config)
                set_metadata(db, "complete", False)

        existing = {ident for (ident,) in db.execute("SELECT id FROM chunks")}
        if not existing.issubset({row["id"] for row in rows}):
            raise ValueError("Index has unexpected IDs. Use a new index path.")
        pending = [row for row in rows if row["id"] not in existing]
        dimensions = saved.get("dimensions")
        count = len(existing)
        print(f"Already saved: {count}/{len(rows)}", flush=True)

        for start in range(0, len(pending), batch_size):
            batch = pending[start:start + batch_size]
            vectors = embed_batch(batch)
            if dimensions is None:
                dimensions = len(vectors[0])
            if any(len(vector) != dimensions for vector in vectors):
                raise ValueError("Embedding dimensions changed. Batch was not saved.")
            # Each batch is committed together. A rerun skips successfully saved rows.
            with db:
                for row, vector in zip(batch, vectors):
                    db.execute("INSERT INTO chunks VALUES (?, ?, ?, ?)", (
                        row["id"], row["text"], json_text(row["metadata"]), json_text(vector)))
                set_metadata(db, "dimensions", dimensions)
            count += len(batch)
            print(f"Saved {count}/{len(rows)}", flush=True)

        stored_count = db.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
        if stored_count != len(rows):
            raise ValueError("Index count does not match the selected data.")
        with db:
            set_metadata(db, "complete", True)
        print(f"Index complete: {stored_count} entries, {dimensions} dimensions")
        print("Index file:", index_path)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path,
                        default=root / "data/processed/openjlpt/grammar.rag.jsonl")
    parser.add_argument("--index", type=Path,
                        default=root / "data/indexes/grammar.sqlite3")
    parser.add_argument("--batch-size", type=int, default=16)
    args = parser.parse_args()
    try:
        rows = load_grammar(args.file)
        print(f"Selected {len(rows)} main grammar entries.", flush=True)
        build_index(rows, args.index, args.batch_size)
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        parser.exit(1, f"Ollama HTTP {exc.code}: {detail}\n")
    except (error.URLError, TimeoutError) as exc:
        parser.exit(1, f"Cannot reach Ollama. Open it and retry. Details: {exc}\n")
    except (OSError, ValueError, KeyError, IndexError, TypeError, sqlite3.Error) as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
