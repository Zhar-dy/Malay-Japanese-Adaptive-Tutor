import sys
from pathlib import Path

RAG_DIR = Path(__file__).resolve().parents[2] / "scripts" / "rag" #"scripts\rag"
if str(RAG_DIR) not in sys.path:
    sys.path.insert(0, str(RAG_DIR))  # Add the rag scripts dir to sys.path so we can import from it.

# These imports only work after the sys.path line above.
from build_grammar_index import MODEL as EMBEDDING_MODEL
from search_grammar_index import load_index, embed_question, rank_entries
from ask_grammar_tutor import SYSTEM_PROMPT, citation_warnings, parse_ollama_tutor_response

LEVELS = ["N5", "N4", "N3", "N2", "N1"] # Ranked by easiest(N5) to hardest(N1)

def allowed_levels(level, level_mode="exact"):
    """Return the JLPT levels to search. None mean serch every lvl"""
    if level is None:
        return None
    if level_mode == "exact":
        return [level]
    # "at_or_below": N4 -> ["N5", "N4"]
    return LEVELS[: LEVELS.index(level) + 1]

def filter_entries(entries, levels):
    """Filter the entries by the allowed JLPT levels."""
    if levels is None:
        return entries
    return  [entry for entry in entries if entry["metadata"]["jlpt_level"] in levels]

def format_hit(number, hit):
        """Turn one hit from rank_entries() into the shape the API sends to the browser."""
        metadata = hit["metadata"]
        return {
        "ref": f"S{number}",
        "chunk_id": hit["id"],
        "jlpt_level": metadata["jlpt_level"],
        "pattern": metadata.get("pattern"),
        "score": hit["score"],
        "text": hit["text"],
        "source_url": metadata.get("source_url"),
    }