"""Prompts sent to the language model."""
import json

from backend.app import rag_adapter

ENGLISH_LINE = "Pengecualian: tulis penerangan dalam Bahasa Inggeris (English), bukan Bahasa Melayu.\n"


def system_prompt(explain_lang="ms"):
    """The CLI's SYSTEM_PROMPT unchanged, plus one line when English is chosen."""
    if explain_lang == "en":
        return rag_adapter.SYSTEM_PROMPT + ENGLISH_LINE
    return rag_adapter.SYSTEM_PROMPT


def ask_messages(question, sources, explain_lang="ms"):
    """Build the same two messages as ask_grammar_tutor.generate_answer()."""
    reference_data = [
        {"reference": s["ref"], "chunk_id": s["chunk_id"],
         "jlpt_level": s["jlpt_level"], "text": s["text"]}
        for s in sources
    ]
    user_content = json.dumps(
        {"question": question, "reference_data": reference_data}, ensure_ascii=False)
    return [
        {"role": "system", "content": system_prompt(explain_lang)},
        {"role": "user", "content": user_content},
    ]