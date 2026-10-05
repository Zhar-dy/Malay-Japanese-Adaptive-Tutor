# Data Preparation

## Current Status

### OpenJLPT
✅ Downloaded  
✅ Vocabulary and grammar processed  
✅ Schema standardized  
✅ Validation completed  
✅ Malay localization workflow tested  
🟡 Full Malay localization still ongoing  

**Status:** Ready for RAG development

### WJTSentDiL
✅ Dataset inspected  
✅ 100,000 balanced sentences prepared  
✅ Train / validation / test split created  
✅ Duplicate and leakage checks completed  
✅ Validation completed  

**Status:** Ready for Japanese BERT development

---

## 1. OpenJLPT

OpenJLPT is used as the main knowledge source for the Retrieval-Augmented Generation (RAG) component.

The processed data includes:

- Vocabulary
- Grammar
- Example sentences
- Readings
- Romaji
- English meanings
- JLPT levels

The original dataset is kept unchanged in:

```text
data/raw/OpenJLPT/
```

Processed files:

```text
data/processed/openjlpt/
├── vocabulary.json
└── grammar.json
```

### OpenJLPT Results

Vocabulary:

| JLPT Level | Records |
|---|---:|
| N5 | 674 |
| N4 | 630 |
| N3 | 1,659 |
| N2 | 1,778 |
| N1 | 3,070 |
| **Total** | **7,811** |

Grammar:

| JLPT Level | Records |
|---|---:|
| N5 | 81 |
| N4 | 98 |
| N3 | 101 |
| N2 | 123 |
| N1 | 123 |
| **Total** | **526** |

Validation:

```text
Missing critical vocabulary fields: 0
Missing critical grammar fields: 0
Duplicate vocabulary IDs: 0
Duplicate grammar IDs: 0

Vocabulary with examples: 7,245 / 7,811
Grammar with examples: 526 / 526
```

---

## 2. Malay Localization

Malay fields were added to support Malaysian learners.

The localization workflow is:

```text
OpenJLPT
   ↓
English content
   ↓
DeepL EN → MS
   ↓
Malaysian Malay naturalization
   ↓
Review
   ↓
Localized RAG data
```

Example:

```text
Machine translation:
Gaun sekolah musim panas saya bercorak kotak-kotak biru dan putih.

Naturalized Malay:
Baju sekolah musim panas saya bercorak kotak-kotak biru dan putih.
```

A small localization sample was prepared first:

```text
Vocabulary: 40 records
Grammar: 20 records
Total: 60 records
```

Machine translation is treated as a first-pass translation and not final verified linguistic ground truth.

---

## 3. WJTSentDiL

WJTSentDiL is used as training data for the Japanese BERT-based JLPT Proficiency Level Estimator.

A balanced subset of 100,000 Japanese sentences was prepared:

| JLPT Level | Sentences |
|---|---:|
| N5 | 20,000 |
| N4 | 20,000 |
| N3 | 20,000 |
| N2 | 20,000 |
| N1 | 20,000 |
| **Total** | **100,000** |

Dataset split:

```text
Training:   80,000
Validation: 10,000
Testing:    10,000
```

Validation results:

```text
Missing sentences: 0
Missing labels: 0

Duplicate train sentences: 0
Duplicate validation sentences: 0
Duplicate test sentences: 0

Train ↔ Validation overlap: 0
Train ↔ Test overlap: 0
Validation ↔ Test overlap: 0

Invalid JLPT labels: 0
```

Sentence length:

```text
Minimum: 5 characters
Maximum: 100 characters
Average: 21.44 characters
```

Processed files:

```text
data/processed/wjtsentdil/
├── train.csv
├── validation.csv
├── test.csv
└── dataset_summary.txt
```

---

## 4. Dataset Roles

The datasets are kept separate because they serve different purposes.

```text
OpenJLPT
   ↓
Vocabulary + Grammar + Examples
   ↓
RAG Knowledge Base


WJTSentDiL
   ↓
Japanese Sentences + N1–N5 Labels
   ↓
Japanese BERT
   ↓
JLPT Proficiency Level Estimator
```

---

## 5. Important Limitations

- Full OpenJLPT Malay localization is still ongoing.
- Malay translations are machine-assisted and require further review.
- WJTSentDiL JLPT labels are retained from the original dataset and are not manually verified ground truth.
- The model estimates learner proficiency; it does not determine an official JLPT certification level.

---

## 6. Next Development Phase

Next tasks:

1. Fine-tune Japanese BERT using WJTSentDiL.
2. Evaluate the JLPT Proficiency Level Estimator.
3. Generate embeddings for OpenJLPT.
4. Build the RAG vector database.
5. Integrate RAG and the estimator into the tutor.

GPU-heavy model training can be performed using Google Colab.