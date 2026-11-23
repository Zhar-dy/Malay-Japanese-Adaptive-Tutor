"""Tests for the judge: plain inputs, no Ollama."""
import unittest

from backend.app.services.judge import matches_reference, normalise

ANSWERS = ["私はご飯を食べます。"]


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


if __name__ == "__main__":
    unittest.main()