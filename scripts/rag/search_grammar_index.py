"""Step 5: search saved grammar vectors by embedding only the question."""
import argparse
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import sys
from urllib import error

# Reuse functions from the earlier steps instead of copying their implementations.
from build_grammar_index import MODEL, model_digest, ollama_api
from compare_grammar_chunks import cosine_similarity


def load_index(index_path):
    if not index_path.is_file():
        raise ValueError("Index missing. Run scripts/rag/build_grammar_index.py first.")
    # Read-only mode prevents searching from modifying the index.
    with closing(sqlite3.connect(index_path.resolve().as_uri() + "?mode=ro", uri=True)) as db:
        info = {key: json.loads(value)
                for key, value in db.execute("SELECT key, value FROM metadata")}
        if not info.get("complete"):
            raise ValueError("Index is incomplete. Rerun the builder to resume.")
        config = info["config"]
        if config["model"] != MODEL or config["format"] != "embeddinggemma-retrieval-v1":
            raise ValueError("This script does not support the index's model or format.")
        entries = [
            {"id": ident, "text": text, "metadata": json.loads(metadata),
             "vector": json.loads(vector)}
            for ident, text, metadata, vector in db.execute(
                "SELECT id, text, metadata_json, embedding_json FROM chunks ORDER BY id")
        ]
    if not entries or len(entries) != config["expected_count"]:
        raise ValueError("The index count does not match its recorded configuration.")
    if any(len(entry["vector"]) != info["dimensions"] for entry in entries):
        raise ValueError("An embedding has the wrong number of dimensions.")
    return info, entries


def embed_question(question, info):
    if model_digest() != info["config"]["model_digest"]:
        raise ValueError("Embedding model changed. Build a NEW index before searching.")
    result = ollama_api("embed", {
        "model": MODEL,
        "input": "task: search result | query: " + question,
        "truncate": False,
        "keep_alive": 0,
    })
    vectors = result["embeddings"]
    if len(vectors) != 1 or len(vectors[0]) != info["dimensions"]:
        raise ValueError("Unexpected query embedding shape.")
    return vectors[0]


def rank_entries(question_vector, entries, top_k):
    ranked = [
        {"id": entry["id"], "text": entry["text"], "metadata": entry["metadata"],
         "score": cosine_similarity(question_vector, entry["vector"])}
        for entry in entries
    ]
    return sorted(ranked, key=lambda hit: (-hit["score"], hit["id"]))[:top_k]


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("question", nargs="?",
                        default="Partikel apakah yang menandakan topik ayat?")
    parser.add_argument("--index", type=Path, default=root / "data/indexes/grammar.sqlite3")
    parser.add_argument("--level", choices=("N5", "N4", "N3", "N2", "N1"))
    parser.add_argument("--top-k", type=int, choices=range(1, 21), default=5)
    args = parser.parse_args()
    try:
        if not args.question.strip():
            raise ValueError("Question must not be empty.")
        info, entries = load_index(args.index)
        print(f"Loaded {len(entries)} saved grammar entries.")
        if args.level:
            entries = [entry for entry in entries
                       if entry["metadata"]["jlpt_level"] == args.level]
        if not entries:
            print("No entries match this level filter.")
            return
        print(f"Searching {len(entries)} entries; embedding only your question...", flush=True)
        vector = embed_question(args.question, info)
        hits = rank_entries(vector, entries, args.top_k)
        print("\nQuestion:", args.question)
        for number, hit in enumerate(hits, start=1):
            print(f"{number}. {hit['id']} | {hit['metadata']['jlpt_level']} "
                  f"| cosine={hit['score']:.4f}")
            print("   Source:", hit["metadata"].get("source_url", "not supplied"))
        print("\nTop retrieved entry:\n" + hits[0]["text"])
        print("\nScores are similarity rankings, not confidence percentages.")
        print("No answer was generated. The saved index was not changed.")
    except error.HTTPError as exc:
        parser.exit(1, f"Ollama HTTP {exc.code}: "
                      f"{exc.read().decode('utf-8', errors='replace')}\n")
    except (error.URLError, TimeoutError) as exc:
        parser.exit(1, f"Cannot reach Ollama. Open it and retry. Details: {exc}\n")
    except (OSError, ValueError, KeyError, IndexError, TypeError, sqlite3.Error) as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
