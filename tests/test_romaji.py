"""Tests for the romaji service (needs pykakasi or cutlet installed)."""
import unittest

from backend.app.services.romaji import has_japanese, to_romaji


class RomajiTests(unittest.TestCase):
    def test_kana_becomes_romaji(self):
        self.assertEqual(to_romaji("ねこ")["romaji"].lower(), "neko")

    def test_engine_name_is_reported(self):
        self.assertIn(to_romaji("ねこ")["romaji_engine"], ("cutlet", "pykakasi"))

    def test_latin_text_has_no_japanese(self):
        self.assertFalse(has_japanese("abc"))
        self.assertFalse(has_japanese(""))

    def test_kanji_kana_and_mixed_text_are_japanese(self):
        for text in ("私", "ねこ", "カタカナ", "Saya suka 寿司"):
            with self.subTest(text=text):
                self.assertTrue(has_japanese(text))

    def test_empty_text_gives_empty_romaji(self):
        self.assertEqual(to_romaji("   ")["romaji"], "")


if __name__ == "__main__":
    unittest.main()