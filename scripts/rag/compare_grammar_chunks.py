"""Step 3: compare a question with three grammar chunks using embeddings."""
import argparse
import json
import math
from pathlib import Path
import sys
from urllib import error, request

CANDIDATES = (
    "openjlpt:grammar:wa",
    "openjlpt:grammar:ga-subject",
    "openjlpt:grammar:o",
)


def load_candidates(file_path):
    chunks = {}
    with file_path.open(encoding="utf-8-sig") as source:
        for line in source:
            if line.strip():
                chunk = json.loads(line)
                if chunk["id"] in CANDIDATES:
                    chunks[chunk["id"]] = chunk
    if len(chunks) != len(CANDIDATES):
        raise ValueError("Expected grammar chunks for wa, ga-subject, and o.")
    return [chunks[ident] for ident in CANDIDATES]


def get_embeddings(question, chunks):
    # Queries and documents have different retrieval prefixes for EmbeddingGemma.
    inputs = ["task: search result | query: " + question]
    for chunk in chunks:
        title = chunk["metadata"].get("pattern", "none")
        inputs.append(f"title: {title} | text: {chunk['text']}")
    payload = {
        "model": "embeddinggemma:300m", "input": inputs,
        "truncate": False, "keep_alive": 0,
    }
    req = request.Request(
        "http://localhost:11434/api/embed",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with request.urlopen(req, timeout=300) as response:
        vectors = json.load(response)["embeddings"]
    if len(vectors) != len(inputs):
        raise ValueError("Ollama returned a different number of vectors than requested.")
    return vectors


def cosine_similarity(left, right):
    if not left or len(left) != len(right):
        raise ValueError("Vectors must be nonempty and have matching lengths.")
    if not all(isinstance(x, (int, float)) and math.isfinite(x) for x in left + right):
        raise ValueError("Invalid vector values.")
    left_length = math.sqrt(sum(x * x for x in left))
    right_length = math.sqrt(sum(x * x for x in right))
    if left_length == 0 or right_length == 0:
        raise ValueError("Cannot compare a zero-length vector.")
    return sum(a * b for a, b in zip(left, right)) / (left_length * right_length)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "question", nargs="?", default="Partikel apakah yang menandakan topik ayat?")
    parser.add_argument(
        "--file", type=Path,
        default=Path(__file__).resolve().parents[2]
        / "data/processed/openjlpt/grammar.rag.jsonl",
    )
    args = parser.parse_args()
    try:
        if not args.question.strip():
            raise ValueError("The question must not be empty.")
        chunks = load_candidates(args.file)
        print("Question:", args.question)
        print("Embedding one question and three grammar chunks...", flush=True)
        vectors = get_embeddings(args.question, chunks)
        question_vector = vectors[0]
        ranked = sorted(
            [(cosine_similarity(question_vector, vector), chunk)
             for chunk, vector in zip(chunks, vectors[1:])],
            key=lambda item: item[0], reverse=True,
        )
        print("\nRanking (higher cosine similarity ranks first):")
        for position, (score, chunk) in enumerate(ranked, start=1):
            print(f"{position}. {chunk['id']} | score={score:.4f}")
        print("\nTop retrieved chunk:")
        print(ranked[0][1]["text"])
        print("\nThis searches only three candidates. No answer was generated or saved.")
    except error.HTTPError as exc:
        parser.exit(1, f"Ollama HTTP {exc.code}: {exc.read().decode('utf-8', errors='replace')}\n")
    except (error.URLError, TimeoutError) as exc:
        parser.exit(1, f"Cannot reach Ollama. Open it and retry. Details: {exc}\n")
    except (OSError, ValueError, KeyError, IndexError, TypeError) as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
