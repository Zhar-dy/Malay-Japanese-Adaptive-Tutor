"""Judging learner attempts: normalise text and match reference answers.

Pure logic: standard library only, no Ollama.
"""
import unicodedata

COMMAS = "、,"
END_PUNCTUATION = "。.!！?？"


def normalise(text):
    """Make two ways of typing the same sentence compare as equal."""
    text = unicodedata.normalize("NFKC", text)
    text = "".join(ch for ch in text if not ch.isspace() and ch not in COMMAS)
    return text.rstrip(END_PUNCTUATION)


def matches_reference(attempt, accepted_answers):
    """True if the attempt equals any accepted answer after normalising."""
    target = normalise(attempt)
    if not target:
        return False
    return any(target == normalise(answer) for answer in accepted_answers)