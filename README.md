# Malay–Japanese Adaptive Tutor

Final Year Project (FYP) for an adaptive Japanese language tutoring system designed for Malaysian learners, curated and developed by **Zhardyz**.

The planned system combines Retrieval-Augmented Generation (RAG), Japanese sentence-difficulty classification, and adaptive teaching strategies to provide explanations in Malay. Learners will be able to use Malay, English, and Japanese.

**Current phase:** Processed datasets published. The grammar RAG prototype now runs as a local web app: the 526 main OpenJLPT-Malay grammar entries are embedded into a local SQLite index, and a FastAPI backend retrieves them and generates Malay explanations with source citations through a local Ollama model. Tiered scaffolding, the BERT sentence-difficulty classifier, audio, and the lecturer evaluation mode are next. No trained-model results or learning-effectiveness results are claimed yet.

## What Works Now

| Part | What it does | Where |
| --- | --- | --- |
| Grammar index | 526 main grammar entries embedded with `embeddinggemma:300m` (768 dimensions) and stored in one SQLite file | `scripts/rag/build_grammar_index.py` |
| Command-line tutor | Search the index, or ask a question and get a Malay explanation | `scripts/rag/` |
| Web API | `POST /api/search` (retrieval only), `POST /api/ask` (retrieval and a Malay answer with `[S1]`-style citations), `GET /api/health` (status of Ollama, the index, and the optional parts) | `backend/app/` |
| Ask page | One page with a question box that shows the answer and its sources | `frontend/index.html` |
| Answer log | Every answered question is saved locally with its sources, prompt, model version, and timings | `data/app/tutor.sqlite3` (not in Git) |
| Tests | 4 RAG tests that use the local index, and 10 API tests that run without Ollama | `tests/` |

Everything runs on the local machine. Retrieval covers grammar only for now; vocabulary is published but not indexed. Answer quality has not been formally evaluated yet.

## Getting Started

1. Build the grammar index and try the command-line scripts: [docs/RAG_SETUP.md](docs/RAG_SETUP.md).
2. Start the web app: [docs/RUNNING.md](docs/RUNNING.md).

Requirements: Python 3.10+ and [Ollama](https://ollama.com) with the `embeddinggemma:300m` and `qwen3.5:4b` models. The web app's Python packages are listed in `requirements-web.txt`; the command-line scripts use only the standard library. Development so far was done on Windows with a 4 GB GPU, where the generation model runs partly on the CPU.

## Repository Layout

```text
backend/app/           FastAPI app: settings, API routes, Ollama client, answer log
frontend/              Static ask page served by the backend
scripts/rag/           Index builder, search, and command-line tutor (reused by the backend)
scripts/openjlpt/      OpenJLPT-Malay preparation and validation
scripts/wjtsentdil/    WJTSentDiL subset preparation and validation
tests/                 Automated tests
docs/                  Setup and running guides
data/                  Dataset notes (processed data, indexes, and logs are not in Git)
```

## Published Datasets

| Dataset | Purpose | Release |
| --- | --- | --- |
| OpenJLPT-Malay | Malay-localized vocabulary, grammar, and retrieval chunks for the RAG knowledge base | [Hugging Face](https://huggingface.co/datasets/zhardyz/OpenJLPT-Malay) |
| WJTSentDiL project subset | Cleaned Japanese sentences with inherited JLPT silver labels for BERT sentence-difficulty experiments | [Hugging Face](https://huggingface.co/datasets/zhardyz/malay-japanese-adaptive-tutor-wjtsentdil) |

These are derivative datasets prepared for this project. Original sources and contributors retain their respective rights. Each release includes its dataset card, licence, attribution notices, citation information, and data manifest.

## Project Goals

- Support Japanese learning for Malaysian learners.
- Accept Malay, English, and Japanese input.
- Retrieve vocabulary and grammar appropriate to the learning activity.
- Provide explanations in Malay.
- Use sentence-difficulty predictions alongside learner responses and performance to inform adaptive support.
- Evaluate retrieval quality, classification performance, and the completed tutoring prototype.

A sentence's predicted JLPT difficulty is not, by itself, a measurement of a learner's proficiency. Learner-level assessment and adaptation require separate design and evaluation.

## Data Preparation and Publication

### OpenJLPT-Malay

[OpenJLPT-Malay](https://huggingface.co/datasets/zhardyz/OpenJLPT-Malay) is an AI-assisted Malay localization and RAG preparation of [OpenJLPT](https://github.com/evanclan/OpenJLPT), covering community-estimated JLPT levels N5–N1.

| File | Contents | Count |
| --- | --- | ---: |
| `vocabulary.ms.json` | Vocabulary master with Malay meanings and example translations (examples include romaji) | 7,809 records |
| `grammar.rag.json` | Grammar master with Malay meanings, explanations, formation rules, and examples (examples include romaji) | 526 records |
| `vocabulary.rag.jsonl` | Vocabulary and example retrieval chunks | 21,419 chunks |
| `grammar.rag.jsonl` | Grammar and example retrieval chunks | 2,052 chunks |
| `example_attribution.csv` | Vocabulary-example mappings to upstream Tatoeba sentence links | 13,610 mappings |
| `human_review_sample.csv` | The 150 examples in the human review sample | 150 rows |

Example coverage:

- Vocabulary: 13,610 examples across 7,206 of 7,809 records; 603 records have no examples.
- Grammar: 1,526 examples across all 526 records.

Preparation includes schema standardization, Malay localization, targeted grammar corrections, a content-safety cleanup, romaji for every example sentence, and generation of separate retrieval chunks. Romaji is automatically generated and has not been manually checked. Programmatic checks cover required fields, ID uniqueness, meaning alignment, parent links, chunk hashes, and consistency between master records and retrieval chunks.

The master JSON files remain the source of truth. RAG chunks are ready for embedding and indexing; they are not embedding vectors or an existing vector database.

**Status:** Published for RAG prototyping. Structural validation does not establish complete linguistic accuracy.

### WJTSentDiL Project Subset

The [published subset](https://huggingface.co/datasets/zhardyz/malay-japanese-adaptive-tutor-wjtsentdil) contains **99,381 Japanese sentences**, retained from an initial class-balanced sample of 100,000 [WJTSentDiL](https://huggingface.co/datasets/bennexx/WJTSentDiL) sentences.

Conservative cleanup excluded or quarantined 472 rows, and a later content-safety pass removed 147 sentences with sexual or vulgar content. Retained sentences and labels were preserved, and rows stayed in their original splits.

| Split | N5 | N4 | N3 | N2 | N1 | Total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Train | 15,886 | 15,949 | 15,970 | 15,938 | 15,753 | 79,496 |
| Validation | 1,984 | 1,995 | 1,999 | 1,998 | 1,964 | 9,940 |
| Test | 1,993 | 1,991 | 2,000 | 1,997 | 1,964 | 9,945 |
| **Total** | **19,863** | **19,935** | **19,969** | **19,933** | **19,681** | **99,381** |

Each CSV contains `sentence` and `level` columns. The classes remain approximately balanced after cleaning; no rebalancing was applied.

Validation covers nonempty values, valid N1–N5 labels, exclusion accounting, preservation of retained text and labels, and duplicate checks within and across splits using exact, NFKC, and punctuation/symbol/whitespace-stripped comparison keys. These checks do not rule out every paraphrase or document-level overlap.

**Label provenance:** The labels were generated by the upstream classifier. They are silver labels, not human-annotated ground truth. Fine-tuning on them is pseudo-label training; performance on the held-out test split measures agreement with those labels.

**Status:** Published for Japanese BERT sentence-difficulty experiments. Independent, reviewed sentence-level evaluation is needed before making stronger claims about JLPT correctness. Grammar-item or vocabulary-item levels should not automatically be treated as difficulty labels for their full example sentences.

## AI Assistance and Review

Most data-preparation work was AI-assisted. Gemini, ChatGPT/Codex, and Claude (Anthropic) supported localization, proposed corrections, scripts, validation, RAG formatting, and documentation. Exact tool/model provenance was not recorded for every entry.

For OpenJLPT-Malay, 150 randomly sampled example sentences (30 per JLPT level; 24 vocabulary and 6 grammar) were manually reviewed against the Japanese, with only minor issues noted. That is about 1% of the roughly 15,100 examples, so the rest is reviewed by AI and programmatic checks only. The dataset card records this review and the programmatic validation. Neither release is claimed to be fully human-verified. Translation, nuance, reading, sentence-boundary, and inherited label errors may remain.

The application code (RAG scripts, web backend, and tests) was also written with AI assistance, and each part was run and tested by the author. Exact tool provenance was not recorded for every file.

## Data Pipeline

```text
OpenJLPT
  → Schema standardization and Malay localization
  → Targeted corrections, content-safety cleanup, and structural validation
  → Romaji added to example sentences
  → Vocabulary / grammar masters and retrieval chunks
  → Published OpenJLPT-Malay release
  → Embedding and SQLite vector index (main grammar entries only)
  → RAG retrieval and Malay explanations (command-line prototype)
  → Local web app: search, ask, and answer logging (bare ask page)
  → Tiered scaffolding in the web tutor [next]
  → Vocabulary retrieval [planned]

WJTSentDiL
  → Initial balanced 100,000-sentence sample and splits
  → Conservative exclusions and validation
  → Content-safety cleanup (147 rows removed)
  → Published 99,381-sentence subset
  → Japanese BERT fine-tuning [next]
  → Independent evaluation [planned]
  → Integration with learner-response assessment [planned]
```

## Development Roadmap

1. ~~Embed and index the OpenJLPT grammar retrieval chunks.~~ Done for the 526 main grammar entries; vocabulary is not indexed yet.
2. ~~Build a command-line RAG prototype.~~ Done; retrieval quality has not been formally evaluated yet.
3. ~~Wrap the RAG pipeline in a local web application (FastAPI backend, static frontend).~~ Done as a bare version: search and ask endpoints, one ask page, and answer logging. Answer quality has not been evaluated yet.
4. Design adaptive scaffolding (tiered hints before full correction) using learner responses and performance.
5. Fine-tune and evaluate a Japanese BERT sentence-difficulty classifier using Google Colab as the training environment; run inference locally on CPU.
6. Add Japanese text, Romaji, and Japanese Text-to-Speech using VOICEVOX.
7. Build a lecturer evaluation mode and evaluate the completed prototype.

Planned features are development goals, not claims of completed implementation.

## Sources, Attribution, and Licensing

### OpenJLPT-Malay

Credit [OpenJLPT contributors and Evan Clan](https://github.com/evanclan/OpenJLPT), together with the upstream sources identified in the release:

- Electronic Dictionary Research and Development Group (EDRDG) for JMdict.
- Jonathan Waller for JLPT resources and level assignments.
- Tatoeba contributors for vocabulary example sentences.
- OpenJLPT contributors for grammar content and corrections.

See the release's [NOTICE.md](https://huggingface.co/datasets/zhardyz/OpenJLPT-Malay/blob/main/NOTICE.md), [upstream notice](https://huggingface.co/datasets/zhardyz/OpenJLPT-Malay/blob/main/UPSTREAM_NOTICE.md), and [example attribution mappings](https://huggingface.co/datasets/zhardyz/OpenJLPT-Malay/blob/main/example_attribution.csv).

### WJTSentDiL

Credit **Enrico Benedetti, Akiko Aizawa, and Florian Boudin**, the [original WJTSentDiL dataset](https://huggingface.co/datasets/bennexx/WJTSentDiL), and their [ACL 2024 paper](https://aclanthology.org/2024.acl-srw.55/). The corpus includes text from Japanese Wikipedia, jpWaC-L, and Tatoeba; their contributors and source-specific terms remain applicable.

The sampled rows do not preserve original article URLs, source sentence IDs, or contributor names. This attribution gap is documented in the [release notice](https://huggingface.co/datasets/zhardyz/malay-japanese-adaptive-tutor-wjtsentdil/blob/main/NOTICE.md); documentation does not itself recover missing source-level provenance.

### Reuse

Both dataset releases carry a **CC BY-SA 4.0** designation with applicable upstream rights and attribution conditions preserved. Consult each release's licence and notices before redistribution or adaptation. Dataset licensing does not automatically determine the licence of this repository's software.

When reusing the data, credit both the original sources and **Zhardyz** for the derivative preparation, link to the relevant release, and indicate your changes. No endorsement by the original data providers, JLPT organizers, or AI-tool providers is implied.
