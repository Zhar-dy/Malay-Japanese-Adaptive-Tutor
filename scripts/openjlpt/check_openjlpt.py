import json
from pathlib import Path
from collections import Counter


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "processed" / "openjlpt"


with open(DATA_DIR / "vocabulary.json", encoding="utf-8") as f:
    vocab = json.load(f)


print("Total vocabulary:", len(vocab))

levels = Counter(item["jlpt_level"] for item in vocab)

print("\nVocabulary by JLPT level:")

for level in ["N5", "N4", "N3", "N2", "N1"]:
    print(level, levels[level])


print("\nExample record:")
print(json.dumps(vocab[0], ensure_ascii=False, indent=2))