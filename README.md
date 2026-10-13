# Adaptive Japanese Tutor

Final Year Project (FYP) for an adaptive Japanese language tutoring system designed for Malaysian learners.

The system aims to provide Japanese learning support using Retrieval-Augmented Generation (RAG), JLPT proficiency estimation, and adaptive teaching strategies.

## Project Goals

- Support Japanese learning for Malaysian learners
- Accept Malay, English, and Japanese input
- Estimate the learner's JLPT proficiency level
- Retrieve JLPT-appropriate vocabulary and grammar
- Provide explanations in Malay
- Adapt learning support based on the learner's proficiency

## Current Progress

### 1. OpenJLPT

OpenJLPT is prepared as the main knowledge source for the RAG system.

Processed:

- 7,811 vocabulary records
- 526 grammar records
- JLPT levels N5 to N1
- Vocabulary and grammar schemas standardized
- Dataset validated
- No missing critical fields
- No duplicate IDs
- Malay localization workflow tested
- Malaysian Malay localization sample prepared

Example sentence coverage:

- 7,245 / 7,811 vocabulary records
- 526 / 526 grammar records

**Status:** Ready for RAG development.

### 2. WJTSentDiL

WJTSentDiL is prepared for training the Japanese BERT-based JLPT Proficiency Level Estimator.

A balanced subset of 100,000 Japanese sentences was prepared:

| JLPT Level | Sentences |
|---|---:|
| N5 | 20,000 |
| N4 | 20,000 |
| N3 | 20,000 |
| N2 | 20,000 |
| N1 | 20,000 |

Dataset split:

- Training: 80,000
- Validation: 10,000
- Testing: 10,000

Validation checks:

- No missing sentences or labels
- No duplicate sentences
- No overlap between dataset splits
- Balanced JLPT classes
- Valid N1-N5 labels

**Status:** Ready for Japanese BERT model development.

## Data Pipeline

```text
OpenJLPT
   ↓
Preprocessing
   ↓
Schema Standardization
   ↓
Validation
   ↓
Malay Localization
   ↓
RAG Knowledge Base


WJTSentDiL
   ↓
Cleaning
   ↓
Balanced N1-N5 Sampling
   ↓
Train / Validation / Test Split
   ↓
Validation
   ↓
Japanese BERT JLPT Estimator
```

## Project Structure

```text
Malay-Japanese_Adaptive_Tutor/
│
├── data/
│   ├── DATA_PREPROCESSING_AND_LOCALIZATION.md
│   └── processed/
│       ├── openjlpt/
│       └── wjtsentdil/
│
├── scripts/
│   ├── process_openjlpt.py
│   ├── validate_openjlpt.py
│   ├── create_localization_sample.py
│   ├── inspect_wjtsentdil.py
│   ├── prepare_wjtsentdil.py
│   └── validate_wjtsentdil.py
│
└── README.md
```

## Planned System

The final prototype is planned to include:

- LLM-based Japanese tutor
- Retrieval-Augmented Generation (RAG)
- JLPT Proficiency Level Estimator
- Adaptive scaffolding
- Malay explanations
- Japanese text and Romaji output
- Japanese Text-to-Speech using Voicevox

## Development Status

**Current Phase: Data Preparation Completed**

Next:

1. Develop the Japanese BERT JLPT Proficiency Level Estimator
2. Prepare the OpenJLPT vector database
3. Develop the RAG pipeline
4. Integrate adaptive tutoring logic
5. Build the user interface
6. Integrate Voicevox
7. Evaluate the prototype

## Data Sources

- [OpenJLPT](https://github.com/evanclan/OpenJLPT) — vocabulary, grammar, and example sentences
- [WJTSentDiL](https://huggingface.co/datasets/bennexx/WJTSentDiL) — Japanese sentence difficulty/JLPT level data

## Notes

Malay localization is currently being developed using English-to-Malay machine translation followed by Malaysian Malay naturalization and review.

The WJTSentDiL labels are retained from the original dataset. The processed subset has been validated for structural consistency, class balance, duplicates, and train/validation/test leakage.
