"""Phase 2 Step 10: which grammar rules does retrieval find for each evaluation case?

Runs retrieval only (no LLM) and writes a table you fill in by hand.
Example (from the project folder, Ollama open):
.venv\\Scripts\\python.exe scripts\\eval\\audit_retrieval.py
"""
import argparse
from pathlib import Path
import sys
from urllib import error

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))  # so "backend.app" can be imported (same trick as rag_adapter.py)

from backend.app import rag_adapter
from backend.app.config import load_settings
from backend.app.services.cases import load_cases

DEFAULT_OUT = ROOT / "data" / "app" / "eval_runs" / "retrieval_audit.md"
TOP_K = 3


def retrieve_for_case(case, info, entries):
    """Same query the practice endpoint will use: meaning + newline + learner attempt."""
    query = case["intended_meaning_ms"] + "\n" + case["learner_input_ja"]
    levels = rag_adapter.allowed_levels(case["target_level"], "at_or_below")
    allowed = rag_adapter.filter_entries(entries, levels)
    vector = rag_adapter.embed_question(query, info)
    return rag_adapter.rank_entries(vector, allowed, TOP_K)


def cell(hit):
    """One table cell: pattern (level, score)."""
    metadata = hit["metadata"]
    return f"{metadata.get('pattern')} ({metadata['jlpt_level']}, {hit['score']:.3f})"


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    settings = load_settings()
    try:
        info, entries = rag_adapter.load_index(settings.index_path)
    except (OSError, ValueError) as exc:
        sys.exit(f"Cannot load the grammar index: {exc}")

    rows = [
        "| Case | Title | S1 | S2 | S3 | Relevant rule? (fill in) |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    first_text = None
    for case in load_cases():
        try:
            hits = retrieve_for_case(case, info, entries)
        except (error.URLError, TimeoutError) as exc:
            sys.exit(f"Cannot reach Ollama. Open it and retry. ({exc})")
        cells = [cell(hit) for hit in hits] + [""] * (TOP_K - len(hits))
        rows.append(f"| {case['id']} | {case['title']} | " + " | ".join(cells) + " |  |")
        print(f"{case['id']}: " + "; ".join(cells))
        if first_text is None and hits:
            first_text = (case["id"], hits[0]["text"])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("# Retrieval audit (top 3, at or below the case level)\n\n"
                        + "\n".join(rows) + "\n", encoding="utf-8")
    print(f"\nWrote {args.out}")

    if first_text:
        print(f"\nFull text of {first_text[0]} S1, to see what one grammar entry contains:\n")
        print(first_text[1])


if __name__ == "__main__":
    main()