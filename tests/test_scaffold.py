"""Tests for the scaffolding state machine: plain inputs, no Ollama."""
import unittest

from backend.app.services.scaffold import (
    BLOOM_LABELS,
    TIER_LABELS,
    ItemState,
    advance,
    tier_if_wrong,
)

NEW = ItemState()
TIER_1 = ItemState(status="in_progress", tier=1)
TIER_2 = ItemState(status="in_progress", tier=2)


class ScaffoldTests(unittest.TestCase):
    def test_correct_at_start_is_solved_at_tier_0(self):
        state = advance(NEW, "attempt", correct=True)
        self.assertEqual(state.status, "solved")
        self.assertEqual(state.solved_at_tier, 0)

    def test_wrong_at_start_goes_to_tier_1(self):
        state = advance(NEW, "attempt", correct=False)
        self.assertEqual((state.status, state.tier), ("in_progress", 1))

    def test_help_at_tier_1_goes_to_tier_2(self):
        state = advance(TIER_1, "help")
        self.assertEqual((state.status, state.tier), ("in_progress", 2))

    def test_wrong_at_tier_2_reveals_at_tier_3(self):
        state = advance(TIER_2, "attempt", correct=False)
        self.assertEqual((state.status, state.tier), ("revealed", 3))

    def test_correct_at_tier_1_is_solved_at_tier_1(self):
        state = advance(TIER_1, "attempt", correct=True)
        self.assertEqual(state.status, "solved")
        self.assertEqual(state.solved_at_tier, 1)

    def test_help_ignores_correct(self):
        state = advance(TIER_1, "help", correct=True)
        self.assertEqual((state.status, state.tier), ("in_progress", 2))

    def test_finished_items_raise(self):
        for done in (ItemState(status="solved", solved_at_tier=0),
                     ItemState(status="revealed", tier=3)):
            with self.subTest(status=done.status):
                with self.assertRaises(ValueError):
                    advance(done, "attempt", correct=True)

    def test_help_before_any_attempt_raises(self):
        with self.assertRaises(ValueError):
            advance(NEW, "help")

    def test_unknown_event_raises(self):
        with self.assertRaises(ValueError):
            advance(TIER_1, "skip")

    def test_old_state_is_not_changed(self):
        advance(TIER_1, "attempt", correct=False)
        self.assertEqual(TIER_1.tier, 1)

    def test_tier_if_wrong_and_labels(self):
        self.assertEqual(tier_if_wrong(TIER_1), 2)
        self.assertEqual(TIER_LABELS[3], "Pembetulan penuh")
        self.assertEqual(set(BLOOM_LABELS), {1, 2, 3})


if __name__ == "__main__":
    unittest.main()