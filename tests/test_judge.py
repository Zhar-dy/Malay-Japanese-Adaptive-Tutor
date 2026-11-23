"""Tests for the judge: plain inputs, no Ollama."""
import unittest

from backend.app.services.judge import find_leak, leak_patterns, matches_reference, normalise

ANSWERS = ["私はご飯を食べます。"]
LIBRARY_CASE = {"accepted_answers_ja": ["私は図書館で勉強します。"]}
STUDENT_CASE = {"accepted_answers_ja": ["私は学生です。"]}


class NormaliseTests(unittest.TestCase):
    def test_removes_spaces_commas_and_end_punctuation(self):
        self.assertEqual(normalise(" 先生、明日 来ますか？ "), "先生明日来ますか")

    def test_keeps_punctuation_inside_the_text(self):
        self.assertEqual(normalise("はい。そうです。"), "はい。そうです")


class MatchesReferenceTests(unittest.TestCase):
    def test_same_sentence_matches(self):
        self.assertTrue(matches_reference("私はご飯を食べます。", ANSWERS))

    def test_spaces_still_match(self):
        self.assertTrue(matches_reference("私は ご飯を 食べます", ANSWERS))

    def test_full_width_space_still_matches(self):
        self.assertTrue(matches_reference("私は\u3000ご飯を食べます。", ANSWERS))

    def test_exclamation_mark_still_matches(self):
        self.assertTrue(matches_reference("私はご飯を食べます！", ANSWERS))

    def test_wrong_word_order_does_not_match(self):
        self.assertFalse(matches_reference("私は食べますご飯を。", ANSWERS))

    def test_comma_and_question_mark_are_ignored(self):
        self.assertTrue(matches_reference("先生明日来ますか？", ["先生、明日来ますか。"]))

    def test_any_accepted_answer_can_match(self):
        answers = ["わたしはごはんをたべます。", "私はご飯を食べます。"]
        self.assertTrue(matches_reference("私はご飯を食べます", answers))

    def test_empty_attempt_never_matches(self):
        self.assertFalse(matches_reference("  。", ANSWERS))
        self.assertFalse(matches_reference("私はご飯を食べます", []))

class LeakGuardTests(unittest.TestCase):
    def test_patterns_are_full_sentence_and_core_clause(self):
        self.assertEqual(leak_patterns(LIBRARY_CASE), ["私は図書館で勉強します", "図書館で勉強します"])

    def test_full_sentence_leak(self):
        message = "Cuba tulis: 私は図書館で勉強します。"
        self.assertEqual(find_leak(message, leak_patterns(LIBRARY_CASE)), "私は図書館で勉強します")

    def test_core_clause_leak(self):
        message = "Contoh: 図書館で勉強します。"
        self.assertEqual(find_leak(message, leak_patterns(LIBRARY_CASE)), "図書館で勉強します")

    def test_short_core_is_not_a_pattern(self):
        patterns = leak_patterns(STUDENT_CASE)
        self.assertEqual(patterns, ["私は学生です"])
        self.assertIsNone(find_leak("Dia 学生です juga.", patterns))

    def test_case_override_replaces_automatic_patterns(self):
        case = {"accepted_answers_ja": ["私は学生です。"], "leak_patterns_ja": ["学生です。"]}
        patterns = leak_patterns(case)
        self.assertEqual(patterns, ["学生です"])
        self.assertEqual(find_leak("Jawapan: 学生です", patterns), "学生です")

    def test_leak_with_spaces_inside_is_found(self):
        message = "Cuba: 図書館 で 勉強 します"
        self.assertEqual(find_leak(message, leak_patterns(LIBRARY_CASE)), "図書館で勉強します")

    def test_clean_hint_has_no_leak(self):
        message = "Lihat partikel selepas tempat. Di mana kata kerja diletakkan?"
        self.assertIsNone(find_leak(message, leak_patterns(LIBRARY_CASE)))

    def test_empty_patterns_are_ignored(self):
        self.assertEqual(leak_patterns({"accepted_answers_ja": ["。"]}), [])
        self.assertIsNone(find_leak("apa-apa", [""]))

if __name__ == "__main__":
    unittest.main()