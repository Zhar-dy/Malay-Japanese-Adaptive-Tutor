# OpenJLPT Data Preprocessing and Malay Localization Pipeline

## 1. Dataset Selected

The OpenJLPT dataset is used as the primary knowledge source for the Retrieval-Augmented Generation (RAG) component of the Adaptive Japanese Language Tutor.

The dataset contains structured Japanese learning data across JLPT levels N5 to N1, including:

- Vocabulary
- Grammar
- Example sentences
- Readings
- Romaji
- English meanings
- JLPT level information

For this project, the main processed components are:

- Vocabulary
- Grammar

Kanji data is retained in the raw dataset but is not prioritized in the current development phase.

---

## 2. Purpose of the Dataset

The processed OpenJLPT data will be used as the knowledge base for the RAG component.

The RAG system will retrieve suitable Japanese learning content based on the learner's estimated proficiency level and input.

The knowledge base is localized for Malaysian learners by adding Malay translations and explanations while preserving the original Japanese and English information.

---

## 3. Raw Data Storage

The original OpenJLPT dataset is preserved without modification.

Raw dataset location:

```text
data/raw/OpenJLPT/