"""Turn data/supplementary/grammar_extra.json into retrieval chunks (same format as OpenJLPT).

The output file is what build_grammar_index.py reads. Run it again after editing the JSON.
Example (from the project folder):
.venv\\Scripts\\python.exe scripts\\rag\\make_supplementary_chunks.py
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IN = ROOT / "data" / "supplementary" / "grammar_extra.json"
DEFAULT_OUT = ROOT / "data" / "supplementary" / "grammar_extra.rag.jsonl"


def chunk_text(entry):
    """The same line layout as an OpenJLPT grammar chunk, so it is embedded the same way."""
    lines = [
        f"Grammar: {entry['pattern']}",
        f"Romaji: {entry['romaji']}",
        f"Meaning (Malay): {entry['meaning_ms']}",
        f"Explanation (Malay): {entry['explanation_ms']}",
        f"Formation (Malay): {entry['formation_ms']}",
        f"Meaning (English): {entry['meaning_en']}",
        f"Formation (English): {entry['formation_en']}",
        f"Notes (English): {entry['notes_en']}",
    ]
    for number, example in enumerate(entry["examples"], start=1):
        lines.append(f"Example {number} (Japanese): {example['ja']}")
        lines.append(f"Example {number} (Malay): {example['ms']}")
        lines.append(f"Example {number} (English): {example['en']}")
    return "\n".join(lines)


def make_chunk(entry):
    text = chunk_text(entry)
    chunk_id = f"supplementary:grammar:{entry['id']}"
    return {
        "id": chunk_id,
        "text": text,
        "metadata": {
            "record_id": entry["id"],
            "type": "grammar",
            "jlpt_level": entry["jlpt_level"],
            "chunk_type": "grammar",
            "parent_id": chunk_id,
            "pattern": entry["pattern"],
            "romaji": entry["romaji"],
            "tags": entry["tags"],
            "source": "Researcher (supplementary rule)",
            "source_url": None,
            "languages": ["ja", "ms", "en"],
            "review_status": entry["review_status"],
            "human_verified": entry["review_status"] != "DRAFT",
            "content_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--input", type=Path, default=DEFAULT_IN)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    entries = json.loads(args.input.read_text(encoding="utf-8"))
    chunks = [make_chunk(entry) for entry in entries]
    with args.out.open("w", encoding="utf-8", newline="\n") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    print(f"Wrote {len(chunks)} chunk(s) to {args.out}")


if __name__ == "__main__":
    main()