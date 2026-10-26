"""Step 1: read grammar chunks without changing the dataset."""
import argparse
from collections import Counter
import json
import sys
from pathlib import Path


def inspect_chunks(file_path):
    levels = Counter()
    chunk_types = Counter()
    first_chunk = None
    total = 0

    # JSONL stores one JSON object per line, so read each line separately.
    with file_path.open(encoding="utf-8-sig") as source:
        for line_number, line in enumerate(source, start=1):
            if not line.strip():
                continue
            try:
                chunk = json.loads(line)
                metadata = chunk["metadata"]
                level = metadata["jlpt_level"]
                chunk_type = metadata["chunk_type"]
                # These are the fields we will need for retrieval later.
                if not chunk["id"] or not chunk["text"]:
                    raise ValueError("A chunk needs an ID and text.")
            except (ValueError, KeyError, TypeError) as error:
                raise ValueError(f"Check line {line_number}: {error}") from error

            total += 1
            levels[level] += 1
            chunk_types[chunk_type] += 1
            if first_chunk is None:
                first_chunk = chunk

    if first_chunk is None:
        raise ValueError("The file has no chunks.")

    print(f"File: {file_path}")
    print(f"Total chunks: {total}")
    print("Chunk types:", dict(chunk_types))
    print("JLPT levels:", dict(levels))
    print("\nFirst chunk:")
    print("ID:", first_chunk["id"])
    print("Metadata:", json.dumps(first_chunk["metadata"], ensure_ascii=False, indent=2))
    print("\nText:")
    print(first_chunk["text"])


def main():
    # Print Japanese correctly even when Windows defaults to another encoding.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    project_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--file", type=Path,
        default=project_root / "data/processed/openjlpt/grammar.rag.jsonl")
    args = parser.parse_args()
    try:
        inspect_chunks(args.file)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()
