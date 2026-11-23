"""Tests for the evaluation cases file (reads the real data/eval/cases.json)."""
import unittest

from backend.app.services.cases import REQUIRED_KEYS, get_case, load_cases
from backend.app.services.judge import matches_reference

CASES = load_cases()
ERROR_CATEGORIES = {"word_order", "particle", "verb_form", "politeness",
                    "copula", "vocabulary", "other"}


class CasesFileTests(unittest.TestCase):
    def test_there_are_ten_cases(self):
        self.assertEqual(len(CASES), 10)

    def test_ids_are_case_01_to_case_10(self):
        expected = [f"case-{number:02d}" for number in range(1, 11)]
        self.assertEqual([case["id"] for case in CASES], expected)

    def test_every_case_has_every_key(self):
        for case in CASES:
            with self.subTest(case=case["id"]):
                for key in REQUIRED_KEYS:
                    self.assertIn(key, case)

    def test_every_case_has_an_accepted_answer(self):
        for case in CASES:
            with self.subTest(case=case["id"]):
                self.assertGreaterEqual(len(case["accepted_answers_ja"]), 1)

    def test_learner_input_is_really_wrong(self):
        for case in CASES:
            with self.subTest(case=case["id"]):
                self.assertFalse(matches_reference(case["learner_input_ja"],
                                                   case["accepted_answers_ja"]))

    def test_every_case_is_still_a_draft(self):
        for case in CASES:
            with self.subTest(case=case["id"]):
                self.assertEqual(case["review_status"], "DRAFT")

    def test_error_category_is_known(self):
        for case in CASES:
            with self.subTest(case=case["id"]):
                self.assertIn(case["error_category"], ERROR_CATEGORIES)


class GetCaseTests(unittest.TestCase):
    def test_finds_a_case(self):
        self.assertEqual(get_case(CASES, "case-04")["learner_input_ja"], "私は図書館に勉強します。")

    def test_unknown_id_gives_none(self):
        self.assertIsNone(get_case(CASES, "case-99"))


if __name__ == "__main__":
    unittest.main()