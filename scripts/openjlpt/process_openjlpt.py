import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

RAW_DIR = BASE_DIR / "data" / "raw" / "OpenJLPT" / "data" / "json"
OUTPUT_DIR = BASE_DIR / "data" / "processed" / "openjlpt"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

LEVELS = ["n5", "n4", "n3", "n2", "n1"]


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def process_vocabulary():
    output = []

    for level in LEVELS:
        file_path = RAW_DIR / "vocab" / f"{level}.json"
        data = load_json(file_path)

        for item in data:
            examples = []

            for example in item.get("examples", []):
                examples.append({
                    "japanese": example.get("ja", ""),
                    "english": example.get("en", ""),
                    "malay": ""
                })

            output.append({
                "id": item.get("id"),
                "type": "vocabulary",
                "word": item.get("word", ""),
                "reading": item.get("reading", ""),
                "romaji": item.get("romaji", ""),
                "meaning_en": item.get("meanings", []),
                "meaning_ms": [],
                "jlpt_level": item.get("level", level.upper()),
                "part_of_speech": item.get("pos", []),
                "examples": examples,
                "source": "OpenJLPT"
            })

    save_json(OUTPUT_DIR / "vocabulary.json", output)
    print(f"Vocabulary processed: {len(output)}")


def process_grammar():
    output = []

    for level in LEVELS:
        file_path = RAW_DIR / "grammar" / f"{level}.json"
        data = load_json(file_path)

        for item in data:
            examples = []

            for example in item.get("examples", []):
                examples.append({
                    "japanese": example.get("ja", ""),
                    "english": example.get("en", ""),
                    "malay": ""
                })

            output.append({
                "id": item.get("id"),
                "type": "grammar",
                "pattern": item.get("pattern", ""),
                "romaji": item.get("romaji", ""),
                "meaning_en": item.get("meaning", ""),
                "meaning_ms": "",
                "explanation_ms": "",
                "formation": item.get("formation", ""),
                "jlpt_level": item.get("level", level.upper()),
                "examples": examples,
                "tags": item.get("tags", []),
                "notes": item.get("notes", ""),
                "source": "OpenJLPT"
            })

    save_json(OUTPUT_DIR / "grammar.json", output)
    print(f"Grammar processed: {len(output)}")


if __name__ == "__main__":
    process_vocabulary()
    process_grammar()

    print("OpenJLPT preprocessing complete.")