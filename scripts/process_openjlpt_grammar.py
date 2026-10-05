import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw" / "OpenJLPT" / "data" / "json"
OUTPUT_DIR = BASE_DIR / "data" / "processed" / "openjlpt"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


levels = ["n5", "n4", "n3", "n2", "n1"]

all_grammar = []


for level in levels:
    file_path = RAW_DIR / "grammar" / f"{level}.json"

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data:
        processed = {
            "id": item.get("id"),
            "type": "grammar",
            "pattern": item.get("pattern"),
            "romaji": item.get("romaji"),
            "meaning_en": item.get("meaning"),
            "meaning_ms": "",
            "explanation_ms": "",
            "formation": item.get("formation"),
            "jlpt_level": item.get("level"),
            "examples": item.get("examples", []),
            "tags": item.get("tags", []),
            "notes": item.get("notes"),
            "source": "OpenJLPT"
        }

        all_grammar.append(processed)


output_file = OUTPUT_DIR / "grammar.json"

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(
        all_grammar,
        f,
        ensure_ascii=False,
        indent=2
    )


print(f"Processed {len(all_grammar)} grammar records.")
print(f"Saved to: {output_file}")