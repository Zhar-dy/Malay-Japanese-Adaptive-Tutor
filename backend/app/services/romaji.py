"""Romaji for Japanese text (always shown with the label "auto").

Uses cutlet when it is installed (the engine the dataset's example romaji was made with),
otherwise pykakasi. Every result says which engine made it.
"""
import re

# Hiragana, katakana, kanji and half-width katakana.
JAPANESE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uff66-\uff9f]")

try:
    import cutlet
    _katsu = cutlet.Cutlet()
    ENGINE = "cutlet"
except (ImportError, RuntimeError):
    import pykakasi
    _kakasi = pykakasi.kakasi()
    ENGINE = "pykakasi"


def has_japanese(text):
    """True if the text contains at least one Japanese character."""
    return bool(JAPANESE.search(text))


def to_romaji(text):
    """Return {"romaji": ..., "romaji_engine": ...} for one piece of text."""
    if not text.strip():
        return {"romaji": "", "romaji_engine": ENGINE}
    if ENGINE == "cutlet":
        romaji = _katsu.romaji(text)
    else:
        romaji = " ".join(token["hepburn"] for token in _kakasi.convert(text) if token["hepburn"])
    return {"romaji": romaji.strip(), "romaji_engine": ENGINE}