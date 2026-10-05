# Adaptive Japanese Tutor

Final Year Project (FYP) for an adaptive Japanese language tutoring system designed for Malaysian learners.

The project uses Retrieval-Augmented Generation (RAG) together with JLPT-level estimation to provide Japanese learning support based on the learner's proficiency level.

## Project Goals

- Support Japanese learning for Malaysian learners
- Accept Japanese, English, and Malay input
- Estimate the learner's JLPT proficiency level
- Retrieve JLPT-appropriate vocabulary and grammar
- Provide Malay explanations
- Adapt teaching difficulty using scaffolding principles

## Current Progress

### OpenJLPT Data Preparation

Completed:

- OpenJLPT dataset downloaded and prepared
- Vocabulary data from N5 to N1 combined
- Grammar data from N5 to N1 combined
- Data schema standardized
- Dataset validation completed
- Malay localization pipeline tested
- Malaysian Malay naturalization sample prepared

### Processed Data

Vocabulary:

- 7,811 records
- N5: 674
- N4: 630
- N3: 1,659
- N2: 1,778
- N1: 3,070

Grammar:

- 526 records
- N5: 81
- N4: 98
- N3: 101
- N2: 123
- N1: 123

Validation results:

- 0 missing vocabulary words
- 0 missing readings
- 0 missing romaji
- 0 missing English meanings
- 0 missing JLPT levels
- 0 duplicate vocabulary IDs
- 0 duplicate grammar IDs
- 7,245 vocabulary records contain example sentences
- All 526 grammar records contain example sentences

## Data Pipeline

```text
OpenJLPT
   ↓
Raw JSON Data
   ↓
Preprocessing
   ↓
Schema Standardization
   ↓
Data Validation
   ↓
DeepL EN → MS Translation
   ↓
Malaysian Malay Naturalization
   ↓
Localized RAG Knowledge Base