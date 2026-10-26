import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data" / "processed" / "openjlpt"


def load_json(filename):
    with open(DATA_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(filename, data):
    with open(DATA_DIR / filename, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )


vocab = load_json("vocabulary.json")
grammar = load_json("grammar.json")


# -------------------------
# Vocabulary
# -------------------------

vocab_sample = []

for level in ["N5", "N4"]:
    level_items = [
        item for item in vocab
        if item["jlpt_level"] == level
    ]

    vocab_sample.extend(level_items[:20])


# -------------------------
# Grammar
# -------------------------

grammar_sample = []

for level in ["N5", "N4"]:
    level_items = [
        item for item in grammar
        if item["jlpt_level"] == level
    ]

    grammar_sample.extend(level_items[:10])


save_json(
    "vocabulary_sample_ms.json",
    vocab_sample
)

save_json(
    "grammar_sample_ms.json",
    grammar_sample
)


print("Localization sample created.")
print("Vocabulary:", len(vocab_sample))
print("Grammar:", len(grammar_sample))
print("Total:", len(vocab_sample) + len(grammar_sample))