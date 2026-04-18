"""
Unit tests for the LLM Response Evaluator.
Run with: pytest tests/test_evaluator.py -v
"""

import pytest
from evaluator import ResponseScore, EvaluationRecord


class TestResponseScore:

    def test_average_calculation(self):
        score = ResponseScore(helpfulness=4, accuracy=3, safety=5, conciseness=4, overall=4)
        assert score.average() == 4.0

    def test_average_rounds_correctly(self):
        score = ResponseScore(helpfulness=5, accuracy=3, safety=4, conciseness=3, overall=4)
        assert score.average() == 3.75

    def test_validation_passes_for_valid_scores(self):
        score = ResponseScore(helpfulness=1, accuracy=5, safety=3, conciseness=2, overall=4)
        score.validate()  # Should not raise

    def test_validation_fails_for_zero(self):
        score = ResponseScore(helpfulness=0, accuracy=5, safety=3, conciseness=2, overall=4)
        with pytest.raises(ValueError):
            score.validate()

    def test_validation_fails_for_six(self):
        score = ResponseScore(helpfulness=6, accuracy=5, safety=3, conciseness=2, overall=4)
        with pytest.raises(ValueError):
            score.validate()

    def test_notes_default_empty(self):
        score = ResponseScore(helpfulness=3, accuracy=3, safety=3, conciseness=3, overall=3)
        assert score.notes == ""


class TestEvaluationRecord:

    def _make_record(self, a_scores, b_scores, preferred="A"):
        score_a = ResponseScore(**a_scores)
        score_b = ResponseScore(**b_scores)
        return EvaluationRecord(
            prompt="Test prompt",
            response_a="Response A text",
            response_b="Response B text",
            score_a=score_a,
            score_b=score_b,
            preferred=preferred,
        )

    def test_winner_is_a_when_a_higher(self):
        record = self._make_record(
            {"helpfulness": 5, "accuracy": 5, "safety": 5, "conciseness": 5, "overall": 5},
            {"helpfulness": 3, "accuracy": 3, "safety": 3, "conciseness": 3, "overall": 3},
        )
        assert record.winner() == "A"

    def test_winner_is_b_when_b_higher(self):
        record = self._make_record(
            {"helpfulness": 2, "accuracy": 2, "safety": 2, "conciseness": 2, "overall": 2},
            {"helpfulness": 4, "accuracy": 5, "safety": 5, "conciseness": 4, "overall": 4},
        )
        assert record.winner() == "B"

    def test_winner_is_tie_when_equal(self):
        same = {"helpfulness": 4, "accuracy": 4, "safety": 4, "conciseness": 4, "overall": 4}
        record = self._make_record(same, same)
        assert record.winner() == "tie"

    def test_timestamp_is_set(self):
        same = {"helpfulness": 4, "accuracy": 4, "safety": 4, "conciseness": 4, "overall": 4}
        record = self._make_record(same, same)
        assert record.timestamp != ""

    def test_preferred_stored_correctly(self):
        same = {"helpfulness": 3, "accuracy": 3, "safety": 3, "conciseness": 3, "overall": 3}
        record = self._make_record(same, same, preferred="tie")
        assert record.preferred == "tie"
