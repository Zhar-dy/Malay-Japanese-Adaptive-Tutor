# OpenJLPT Grammar RAG Prototype Setup

This document describes how to set up, build, test, and run the local grammar RAG tutor.

## 1. System Requirements

- **OS:** Windows 10/11, macOS, or Linux
- **Python:** >= 3.10
- **Ollama:** Installed and running locally ([ollama.com](https://ollama.com))

## 2. Models Required

Pull the required models using Ollama:

\`\`\`bash
# Embedding model (768 dimensions)
ollama pull embeddinggemma:300m

# Generation tutor model
ollama pull qwen3.5:4b
\`\`\`

## 3. Knowledge Base & Indexing

The knowledge base is built from `data/processed/openjlpt/grammar.rag.jsonl`.

To create the SQLite vector database (`data/indexes/grammar.sqlite3`):

\`\`\`bash
python scripts/rag/build_grammar_index.py
\`\`\`

*Note: The SQLite database file is excluded from Git tracking via `.gitignore`.*

## 4. Querying & Generation

### Search the Index (Retrieval Only)
\`\`\`bash
python scripts/rag/search_grammar_index.py "Apakah fungsi partikel wa?" --level N5 --top-k 3
\`\`\`

### Ask the RAG Tutor (Retrieval + Generation)
\`\`\`bash
python scripts/rag/ask_grammar_tutor.py "Apakah fungsi partikel wa (は)?" --level N5
\`\`\`

Optional flags:
- `--level N5`: Restrict retrieval to a specific JLPT level (N5 to N1).
- `--top-k 3`: Number of reference sources to supply to the prompt (default: 3).
- `--think`: Enable English chain-of-thought deliberation (disabled by default for speed and token efficiency).
- `--show-thinking`: Print model reasoning trace for developer debugging.

## 5. Running Automated Tests

Run the test suite using Python's built-in `unittest`:

\`\`\`bash
python -m unittest tests/test_rag.py
\`\`\`