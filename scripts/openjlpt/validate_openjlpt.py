import json
from pathlib import Path
from collections import Counter


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "processed" / "openjlpt"


def load_json(filename):
    with open(DATA_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)


vocab = load_json("vocabulary.json")
grammar = load_json("grammar.json")


print("=" * 50)
print("OPENJLPT DATA VALIDATION")
print("=" * 50)

# -----------------------
# 1. TOTAL RECORDS
# -----------------------

print("\n[1] TOTAL RECORDS")
print("Vocabulary:", len(vocab))
print("Grammar:", len(grammar))


# -----------------------
# 2. JLPT DISTRIBUTION
# -----------------------

print("\n[2] VOCABULARY BY JLPT LEVEL")

vocab_levels = Counter(
    item.get("jlpt_level") for item in vocab
)

for level in ["N5", "N4", "N3", "N2", "N1"]:
    print(f"{level}: {vocab_levels[level]}")


print("\n[3] GRAMMAR BY JLPT LEVEL")

grammar_levels = Counter(
    item.get("jlpt_level") for item in grammar
)

for level in ["N5", "N4", "N3", "N2", "N1"]:
    print(f"{level}: {grammar_levels[level]}")


# -----------------------
# 3. MISSING IMPORTANT DATA
# -----------------------

print("\n[4] MISSING VOCABULARY FIELDS")

missing_word = sum(
    1 for item in vocab
    if not item.get("word")
)

missing_reading = sum(
    1 for item in vocab
    if not item.get("reading")
)

missing_romaji = sum(
    1 for item in vocab
    if not item.get("romaji")
)

missing_meaning = sum(
    1 for item in vocab
    if not item.get("meaning_en")
)

missing_level = sum(
    1 for item in vocab
    if not item.get("jlpt_level")
)

print("Missing word:", missing_word)
print("Missing reading:", missing_reading)
print("Missing romaji:", missing_romaji)
print("Missing English meaning:", missing_meaning)
print("Missing JLPT level:", missing_level)


print("\n[5] MISSING GRAMMAR FIELDS")

missing_pattern = sum(
    1 for item in grammar
    if not item.get("pattern")
)

missing_grammar_meaning = sum(
    1 for item in grammar
    if not item.get("meaning_en")
)

missing_formation = sum(
    1 for item in grammar
    if not item.get("formation")
)

missing_grammar_level = sum(
    1 for item in grammar
    if not item.get("jlpt_level")
)

print("Missing pattern:", missing_pattern)
print("Missing English meaning:", missing_grammar_meaning)
print("Missing formation:", missing_formation)
print("Missing JLPT level:", missing_grammar_level)


# -----------------------
# 4. DUPLICATE IDS
# -----------------------

print("\n[6] DUPLICATE IDs")


def count_duplicate_ids(data):
    ids = [
        item.get("id")
        for item in data
        if item.get("id")
    ]

    return len(ids) - len(set(ids))


print(
    "Vocabulary duplicate IDs:",
    count_duplicate_ids(vocab)
)

print(
    "Grammar duplicate IDs:",
    count_duplicate_ids(grammar)
)


# -----------------------
# 5. EXAMPLES
# -----------------------

vocab_with_examples = sum(
    1 for item in vocab
    if item.get("examples")
)

grammar_with_examples = sum(
    1 for item in grammar
    if item.get("examples")
)

print("\n[7] EXAMPLE SENTENCE COVERAGE")

print(
    f"Vocabulary with examples: "
    f"{vocab_with_examples}/{len(vocab)}"
)

print(
    f"Grammar with examples: "
    f"{grammar_with_examples}/{len(grammar)}"
)


# -----------------------
# 6. SAMPLE OUTPUT
# -----------------------

print("\n[8] SAMPLE VOCABULARY RECORD")
print(
    json.dumps(
        vocab[0],
        ensure_ascii=False,
        indent=2
    )
)


print("\n[9] SAMPLE GRAMMAR RECORD")
print(
    json.dumps(
        grammar[0],
        ensure_ascii=False,
        indent=2
    )
)


print("\n" + "=" * 50)
print("VALIDATION COMPLETE")
print("=" * 50)