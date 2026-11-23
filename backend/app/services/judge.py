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


TOPIC_PRONOUNS = ("私は", "わたしは", "僕は", "ぼくは")
MIN_CORE_LENGTH = 5


def core_clause(sentence):
    """The sentence without a leading 私は-style topic, or None if there is none or it is too short."""
    for pronoun in TOPIC_PRONOUNS:
        if sentence.startswith(pronoun):
            core = sentence[len(pronoun):]
            return core if len(core) >= MIN_CORE_LENGTH else None
    return None


def leak_patterns(case):
    """Normalised strings a Tier 1-2 hint must not contain (the answer, or its core clause)."""
    custom = case.get("leak_patterns_ja")
    if custom:
        candidates = custom
    else:
        candidates = []
        for answer in case["accepted_answers_ja"]:
            full = normalise(answer)
            candidates.append(full)
            core = core_clause(full)
            if core:
                candidates.append(core)

    patterns = []
    for text in candidates:
        pattern = normalise(text)
        if pattern and pattern not in patterns:
            patterns.append(pattern)
    return patterns


def find_leak(message, patterns):
    """Return the first pattern found inside the normalised message, or None."""
    text = normalise(message)
    for pattern in patterns:
        if pattern and pattern in text:
            return pattern
    return None