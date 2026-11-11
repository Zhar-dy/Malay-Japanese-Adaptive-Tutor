# Data Preparation

Last updated: 2026-11-11

## Current Status

### OpenJLPT
✅ Downloaded  
✅ Vocabulary and grammar processed  
✅ Schema standardized  
✅ Validation completed  
✅ Malay localization completed (AI-translated and AI-reviewed)  
✅ Content-safety cleanup completed  
✅ Romaji added to all example sentences  
✅ Human sample review completed (150 examples)  
✅ Prepared for Hugging Face upload  
🟡 Not human-verified in full

**Status:** Ready for RAG development

### WJTSentDiL
✅ Dataset inspected  
✅ 100,000 balanced sentences prepared  
✅ Cleanup completed (broken fragments, near-duplicates, conflicting labels)  
✅ Content-safety cleanup completed  
✅ Train / validation / test splits created  
✅ Duplicate and leakage checks completed  
✅ Validation completed  
✅ Prepared for Hugging Face upload  

**Status:** Ready for Japanese BERT development

---

## 1. OpenJLPT

OpenJLPT is used as the main knowledge source for the Retrieval-Augmented Generation (RAG) component.

The processed data includes:

- Vocabulary
- Grammar
- Example sentences (Japanese, romaji, English, Malay)
- Readings
- Romaji (words and example sentences)
- English and Malay meanings
- JLPT levels

The original dataset is kept unchanged in:

```text
data/raw/OpenJLPT/
```

Processed files:

```text
data/processed/openjlpt/
├── vocabulary.ms.json        (master, 7,809 records)
├── vocabulary.rag.jsonl      (RAG chunks, 21,419)
├── grammar.rag.json          (master, 526 records)
├── grammar.rag.jsonl         (RAG chunks, 2,052)
├── human_review_sample.csv   (150 human-reviewed examples)
└── archive/                  (earlier versions and change reports)
```

Upload copies for Hugging Face are in `data/hf_upload/OpenJLPT-Malay/`
(also contains `example_attribution.csv`, `README.md`, `DATA_MANIFEST.json`).

### OpenJLPT Results

Vocabulary:

| JLPT Level | Records |
|---|---:|
| N5 | 674 |
| N4 | 630 |
| N3 | 1,659 |
| N2 | 1,778 |
| N1 | 3,068 |
| **Total** | **7,809** |

Grammar:

| JLPT Level | Records |
|---|---:|
| N5 | 81 |
| N4 | 98 |
| N3 | 101 |
| N2 | 123 |
| N1 | 123 |
| **Total** | **526** |

Examples:

```text
Vocabulary examples: 13,610 (in 7,206 records; 603 records have no examples)
Grammar examples:    1,526 (all 526 records have examples)
Total examples:      15,136
```

RAG chunks:

```text
Vocabulary: 21,419 (7,809 word chunks + 13,610 example chunks)
Grammar:     2,052 (526 grammar chunks + 1,526 example chunks)
All content hashes verify; no orphan parent links.
```

Validation:

```text
Missing critical vocabulary fields: 0
Missing critical grammar fields: 0
Duplicate vocabulary IDs: 0
Duplicate grammar IDs: 0
Examples missing romaji: 0
```

### Changes in the 2026-11-11 update

- Vocabulary went from 7,811 to 7,809 records and from 13,718 to 13,610 examples after a content-safety pass (2 records removed, plus sexual or vulgar glosses and examples at all levels) and removal of examples that did not contain the headword.
- Fifty-five clearly wrong English glosses (N3-N1) were corrected.
- Romaji was added to every example sentence (vocabulary and grammar).
- Grammar example furigana fields (`furigana`, `furigana_status`) were removed and replaced by romaji.

### Romaji

Romaji is generated with cutlet (Hepburn) using fugashi + unidic-lite.

- Grammar examples: word splitting from the Japanese text, kanji readings taken from the prepared furigana.
- Vocabulary examples: generated from the Japanese text only, so words with several readings may occasionally be wrong.
- Romaji is automatically generated and has not been manually checked.

---

## 2. Malay Localization

Malay fields were added to support Malaysian learners.

Current workflow:

```text
OpenJLPT (Japanese + English)
   ↓
AI translation of Malay meanings and example sentences,
done from the Japanese word or sentence
   ↓
AI review and programmatic validation
   ↓
Human sample review (150 examples)
   ↓
Localized RAG data
```

Earlier versions used DeepL EN → MS followed by manual naturalization on a small
sample (60 records: 40 vocabulary, 20 grammar). The word-for-word machine
translations from that stage were replaced with the retranslation above
(N5/N4 first, N3-N1 on 2026-11-11).

Example of the earlier problem:

```text
Machine translation:
Gaun sekolah musim panas saya bercorak kotak-kotak biru dan putih.

Naturalized Malay:
Baju sekolah musim panas saya bercorak kotak-kotak biru dan putih.
```

### Quality and review status

```text
quality_status = ai_reviewed_prototype
human_verified = false  (per record)
```

Human sample review (2026-11-11):

- 150 randomly sampled examples, 30 per level (24 vocabulary + 6 grammar).
- Checked against the Japanese; only minor issues were noted and they were not itemised or corrected.
- 150 of about 15,100 examples is roughly 1% of the data, so it shows the sample was checked but does not prove the whole dataset is correct.
- Sampled entries are listed in `human_review_sample.csv`.

---

## 3. WJTSentDiL

WJTSentDiL is used as training data for the Japanese BERT-based JLPT Proficiency Level Estimator.

A balanced subset of 100,000 Japanese sentences was prepared (20,000 per level),
then cleaned:

```text
Original sample:            100,000
Cleanup 1 (472 removed):     99,528  broken quotes/brackets, near-duplicates,
                                     conflicting labels
Cleanup 2 (147 removed):     99,381  sexual or vulgar content
```

Final sentences per level (all splits):

| JLPT Level | Sentences |
|---|---:|
| N5 | 19,863 |
| N4 | 19,935 |
| N3 | 19,969 |
| N2 | 19,933 |
| N1 | 19,681 |
| **Total** | **99,381** |

Dataset split:

```text
Training:   79,496
Validation:  9,940
Testing:     9,945
```

Classes are close to balanced but no longer exactly equal.

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

Sentence length (final data):

```text
Minimum: 5 characters
Maximum: 100 characters
Average: 21.38 characters
```

Processed files:

```text
data/processed/wjtsentdil/
├── train.csv
├── validation.csv
├── test.csv
├── validation_report.json
├── explicit_content_removed.csv   (hash-only log of the 147 removed rows)
└── archive/                       (original 100k splits and pre-cleanup versions)
```

Upload copies for Hugging Face are in `data/hf_upload/wjtsentdil/`.

Labels are silver labels from the source dataset's classifier. Test accuracy
measures agreement with those labels, not verified JLPT correctness.

---

## 4. Dataset Roles

The datasets are kept separate because they serve different purposes.

```text
OpenJLPT
   ↓
Vocabulary + Grammar + Examples (with romaji)
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

## 5. Publication

| Dataset | Hugging Face |
|---|---|
| OpenJLPT-Malay | `zhardyz/OpenJLPT-Malay` |
| WJTSentDiL-Cleaned | `zhardyz/malay-japanese-adaptive-tutor-wjtsentdil` |

Both are derived datasets released under CC BY-SA 4.0 with source credits, a
change description and AI-assistance disclosure in their README files.
`DATA_MANIFEST.json` in each folder holds SHA-256 hashes of the data files.

---

## 6. Important Limitations

- Malay translations are AI-generated and AI-reviewed; only about 1% of examples were human-checked, with minor issues only.
- Romaji is auto-generated and unchecked; occasional reading or spacing errors are possible.
- OpenJLPT JLPT levels are unofficial community estimates.
- WJTSentDiL JLPT labels are classifier-generated silver labels, not manually verified ground truth.
- The keyword-based content-safety scans do not guarantee that no unsuitable sentence remains.
- The model estimates learner proficiency; it does not determine an official JLPT certification level.

---

## 7. Next Development Phase

Next tasks:

1. Fine-tune Japanese BERT using WJTSentDiL.
2. Evaluate the JLPT Proficiency Level Estimator.
3. Generate embeddings for OpenJLPT.
4. Build the RAG vector database.
5. Integrate RAG and the estimator into the tutor.

GPU-heavy model training can be performed using Google Colab.
