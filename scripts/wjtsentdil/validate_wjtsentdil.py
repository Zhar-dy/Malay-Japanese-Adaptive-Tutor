import pandas as pd
import os

DATA_DIR = "data/processed/wjtsentdil"

train_path = os.path.join(DATA_DIR, "train.csv")
validation_path = os.path.join(DATA_DIR, "validation.csv")
test_path = os.path.join(DATA_DIR, "test.csv")

train = pd.read_csv(train_path)
validation = pd.read_csv(validation_path)
test = pd.read_csv(test_path)

print("=" * 50)
print("WJTSentDiL DATA VALIDATION")
print("=" * 50)

# -----------------------------------------
# 1. TOTAL RECORDS
# -----------------------------------------

print("\n[1] TOTAL RECORDS")

print(f"Train: {len(train)}")
print(f"Validation: {len(validation)}")
print(f"Test: {len(test)}")

total = len(train) + len(validation) + len(test)

print(f"Total: {total}")

# -----------------------------------------
# 2. CLASS DISTRIBUTION
# -----------------------------------------

print("\n[2] TRAIN CLASS DISTRIBUTION")
print(train["level"].value_counts().sort_index())

print("\n[3] VALIDATION CLASS DISTRIBUTION")
print(validation["level"].value_counts().sort_index())

print("\n[4] TEST CLASS DISTRIBUTION")
print(test["level"].value_counts().sort_index())

# -----------------------------------------
# 3. MISSING VALUES
# -----------------------------------------

print("\n[5] MISSING VALUES")

print("Train missing sentences:",
      train["sentence"].isna().sum())

print("Train missing levels:",
      train["level"].isna().sum())

print("Validation missing sentences:",
      validation["sentence"].isna().sum())

print("Validation missing levels:",
      validation["level"].isna().sum())

print("Test missing sentences:",
      test["sentence"].isna().sum())

print("Test missing levels:",
      test["level"].isna().sum())

# -----------------------------------------
# 4. DUPLICATES WITHIN EACH SPLIT
# -----------------------------------------

print("\n[6] DUPLICATES WITHIN SPLITS")

print(
    "Train duplicate sentences:",
    train["sentence"].duplicated().sum()
)

print(
    "Validation duplicate sentences:",
    validation["sentence"].duplicated().sum()
)

print(
    "Test duplicate sentences:",
    test["sentence"].duplicated().sum()
)

# -----------------------------------------
# 5. DATA LEAKAGE BETWEEN SPLITS
# -----------------------------------------

print("\n[7] CROSS-SPLIT DUPLICATES / DATA LEAKAGE")

train_sentences = set(train["sentence"])
validation_sentences = set(validation["sentence"])
test_sentences = set(test["sentence"])

train_validation_overlap = (
    train_sentences & validation_sentences
)

train_test_overlap = (
    train_sentences & test_sentences
)

validation_test_overlap = (
    validation_sentences & test_sentences
)

print(
    "Train ↔ Validation overlap:",
    len(train_validation_overlap)
)

print(
    "Train ↔ Test overlap:",
    len(train_test_overlap)
)

print(
    "Validation ↔ Test overlap:",
    len(validation_test_overlap)
)

# -----------------------------------------
# 6. VALID LABELS
# -----------------------------------------

print("\n[8] VALID LABEL CHECK")

valid_levels = {"N1", "N2", "N3", "N4", "N5"}

all_levels = set(
    pd.concat([
        train["level"],
        validation["level"],
        test["level"]
    ])
)

invalid_levels = all_levels - valid_levels

print("Invalid levels:", invalid_levels)

# -----------------------------------------
# 7. SENTENCE LENGTH
# -----------------------------------------

combined = pd.concat(
    [train, validation, test],
    ignore_index=True
)

combined["length"] = (
    combined["sentence"]
    .astype(str)
    .str.len()
)

print("\n[9] SENTENCE LENGTH")

print(
    "Minimum:",
    combined["length"].min()
)

print(
    "Maximum:",
    combined["length"].max()
)

print(
    "Average:",
    round(combined["length"].mean(), 2)
)

# -----------------------------------------
# 8. SAMPLE RECORDS
# -----------------------------------------

print("\n[10] SAMPLE RECORDS")

for level in ["N5", "N4", "N3", "N2", "N1"]:

    sample = combined[
        combined["level"] == level
    ].iloc[0]

    print(
        f"{level}: {sample['sentence']}"
    )

print("\n" + "=" * 50)
print("VALIDATION COMPLETE")
print("=" * 50)