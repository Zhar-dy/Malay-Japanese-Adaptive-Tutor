from datasets import load_dataset
import pandas as pd
import random
import os
import re

# =========================================================
# CONFIGURATION
# =========================================================

TARGET_PER_LEVEL = 20000
LEVELS = ["N5", "N4", "N3", "N2", "N1"]
SEED = 42

OUTPUT_DIR = "data/processed/wjtsentdil"

os.makedirs(OUTPUT_DIR, exist_ok=True)

random.seed(SEED)

# =========================================================
# LOAD DATASET USING STREAMING
# =========================================================

print("Loading WJTSentDiL...")

dataset = load_dataset(
    "bennexx/WJTSentDiL",
    "main_data",
    split="train",
    streaming=True
)

# Approximate randomization while streaming
dataset = dataset.shuffle(
    seed=SEED,
    buffer_size=100000
)

# =========================================================
# STORAGE
# =========================================================

samples = {level: [] for level in LEVELS}
seen_sentences = set()

# Japanese characters:
# Hiragana, Katakana, Kanji
japanese_pattern = re.compile(
    r"[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]"
)

# =========================================================
# CLEAN AND SAMPLE
# =========================================================

print("Collecting balanced samples...")

processed = 0

for row in dataset:

    processed += 1

    sentence = row.get("sentence")
    level = row.get("level")

    # Invalid level
    if level not in LEVELS:
        continue

    # Already have enough for this level
    if len(samples[level]) >= TARGET_PER_LEVEL:
        continue

    # Missing sentence
    if not sentence:
        continue

    sentence = sentence.strip()

    # Very short sentences
    if len(sentence) < 3:
        continue

    # Very long sentences
    if len(sentence) > 300:
        continue

    # Must contain Japanese characters
    if not japanese_pattern.search(sentence):
        continue

    # Remove exact duplicate sentences
    if sentence in seen_sentences:
        continue

    seen_sentences.add(sentence)

    samples[level].append({
        "sentence": sentence,
        "level": level
    })

    # Print progress every 5,000 accepted records
    total_collected = sum(len(v) for v in samples.values())

    if total_collected % 5000 == 0:
        print("\nCollected:", total_collected)

        for lv in LEVELS:
            print(f"{lv}: {len(samples[lv])}")

    # Stop once all levels reach target
    if all(
        len(samples[level]) >= TARGET_PER_LEVEL
        for level in LEVELS
    ):
        break


# =========================================================
# CHECK RESULTS
# =========================================================

print("\n===================================")
print("SAMPLING COMPLETE")
print("===================================")

for level in LEVELS:
    print(f"{level}: {len(samples[level])}")

total = sum(len(v) for v in samples.values())

print(f"\nTotal records: {total}")
print(f"Rows scanned: {processed}")

# =========================================================
# SPLIT EACH LEVEL
#
# 80% Train
# 10% Validation
# 10% Test
# =========================================================

train_rows = []
validation_rows = []
test_rows = []

for level in LEVELS:

    rows = samples[level]

    random.shuffle(rows)

    train_end = int(len(rows) * 0.80)
    validation_end = int(len(rows) * 0.90)

    train_rows.extend(rows[:train_end])
    validation_rows.extend(rows[train_end:validation_end])
    test_rows.extend(rows[validation_end:])


# Shuffle combined datasets
random.shuffle(train_rows)
random.shuffle(validation_rows)
random.shuffle(test_rows)

# =========================================================
# SAVE CSV FILES
# =========================================================

train_df = pd.DataFrame(train_rows)
validation_df = pd.DataFrame(validation_rows)
test_df = pd.DataFrame(test_rows)

train_path = os.path.join(
    OUTPUT_DIR,
    "train.csv"
)

validation_path = os.path.join(
    OUTPUT_DIR,
    "validation.csv"
)

test_path = os.path.join(
    OUTPUT_DIR,
    "test.csv"
)

train_df.to_csv(
    train_path,
    index=False,
    encoding="utf-8-sig"
)

validation_df.to_csv(
    validation_path,
    index=False,
    encoding="utf-8-sig"
)

test_df.to_csv(
    test_path,
    index=False,
    encoding="utf-8-sig"
)

# =========================================================
# CREATE SUMMARY FILE
# =========================================================

summary_path = os.path.join(
    OUTPUT_DIR,
    "dataset_summary.txt"
)

with open(summary_path, "w", encoding="utf-8") as f:

    f.write("WJTSentDiL Processed Dataset Summary\n")
    f.write("====================================\n\n")

    f.write("Source: bennexx/WJTSentDiL\n")
    f.write("Subset: main_data\n\n")

    f.write("Purpose:\n")
    f.write(
        "Training data for Japanese BERT JLPT "
        "Proficiency Level Estimator.\n\n"
    )

    f.write("Cleaning performed:\n")
    f.write("- Removed empty sentences\n")
    f.write("- Removed exact duplicate sentences\n")
    f.write("- Removed sentences shorter than 3 characters\n")
    f.write("- Removed sentences longer than 300 characters\n")
    f.write("- Required Japanese characters\n")
    f.write("- Balanced JLPT classes\n\n")

    f.write("Class distribution:\n")

    for level in LEVELS:
        f.write(
            f"{level}: {len(samples[level])}\n"
        )

    f.write(f"\nTotal: {total}\n\n")

    f.write("Dataset Split:\n")
    f.write(
        f"Training: {len(train_df)} records\n"
    )
    f.write(
        f"Validation: {len(validation_df)} records\n"
    )
    f.write(
        f"Testing: {len(test_df)} records\n"
    )

print("\nFiles saved:")
print(train_path)
print(validation_path)
print(test_path)
print(summary_path)