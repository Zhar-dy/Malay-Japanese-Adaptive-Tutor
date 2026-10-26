"""Step 2: turn one real grammar chunk into an embedding through Ollama."""
import argparse
import json
import math
from pathlib import Path
import sys
from urllib import error, request


def read_first_chunk(file_path):
    with file_path.open(encoding="utf-8-sig") as source:
        for line in source:
            if line.strip():
                return json.loads(line)
    raise ValueError("The grammar file is empty.")


def embed_chunk(chunk):
    # EmbeddingGemma uses this document prefix for retrieval.
    title = chunk["metadata"].get("pattern", "none")
    document = f"title: {title} | text: {chunk['text']}"
    payload = {
        "model": "embeddinggemma:300m",
        "input": document,
        "truncate": False,
        "keep_alive": 0,
    }

    # Send UTF-8 JSON to the Ollama server running on your own computer.
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        "http://localhost:11434/api/embed",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    with request.urlopen(req, timeout=300) as response:
        result = json.load(response)

    vector = result["embeddings"][0]
    if not vector or not all(
        isinstance(value, (int, float)) and math.isfinite(value) for value in vector
    ):
        raise ValueError("Ollama returned an invalid embedding.")
    return vector


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    project_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--file", type=Path,
        default=project_root / "data/processed/openjlpt/grammar.rag.jsonl",
    )
    args = parser.parse_args()

    try:
        chunk = read_first_chunk(args.file)
        print("Chunk ID:", chunk["id"], flush=True)
        print("Sending this chunk to Ollama...", flush=True)
        vector = embed_chunk(chunk)
        print("Vector length:", len(vector))
        print("First 8 numbers:", [round(value, 6) for value in vector[:8]])
        print("Embedding received. No files were changed or saved.")
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        parser.exit(1, f"Ollama HTTP {exc.code}: {detail}\n")
    except (error.URLError, TimeoutError) as exc:
        parser.exit(1, f"Cannot reach Ollama. Open the Ollama app and retry. Details: {exc}\n")
    except (OSError, ValueError, KeyError, IndexError, TypeError) as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
