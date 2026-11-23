"""The 10 evaluation cases, loaded from data/eval/cases.json."""
import json
from pathlib import Path

# services -> app -> backend -> repo root
DEFAULT_PATH = Path(__file__).resolve().parents[3] / "data" / "eval" / "cases.json"

REQUIRED_KEYS = (
    "id", "title", "error_category",
    "intended_meaning_ms", "intended_meaning_en",
    "learner_input_ja", "accepted_answers_ja", "leak_patterns_ja",
    "target_level", "context_note", "review_status",
)


def load_cases(path=DEFAULT_PATH):
    """Read the cases file. Raise ValueError if a case is missing a key."""
    with open(path, encoding="utf-8") as f:
        cases = json.load(f)
    for case in cases:
        missing = [key for key in REQUIRED_KEYS if key not in case]
        if missing:
            raise ValueError(f"{case.get('id', '?')} is missing {missing}")
    return cases


def get_case(cases, case_id):
    """Return the case with this id, or None if there is none."""
    for case in cases:
        if case["id"] == case_id:
            return case
    return None