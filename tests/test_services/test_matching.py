"""Tests for the matching engine scoring logic."""
from datetime import date, timedelta
from unittest.mock import MagicMock

from backend.services.matching import (
    _jaccard,
    _keyword_score,
    _field_score,
    _career_stage_score,
    _deadline_score,
    compute_match_score,
)


def test_jaccard_empty():
    assert _jaccard(set(), set()) == 0.0


def test_jaccard_identical():
    assert _jaccard({"a", "b"}, {"a", "b"}) == 1.0


def test_jaccard_partial():
    score = _jaccard({"a", "b", "c"}, {"b", "c", "d"})
    assert abs(score - 0.5) < 0.01  # 2/4


def test_keyword_score():
    score, overlap = _keyword_score({"ml", "nlp", "cv"}, {"nlp", "cv", "robotics"})
    assert len(overlap) == 2
    assert "cv" in overlap and "nlp" in overlap


def test_career_stage_eligible():
    score, reason = _career_stage_score("postdoc", "phd_student,postdoc,early_career")
    assert score == 1.0
    assert reason == "eligible"


def test_career_stage_ineligible():
    score, reason = _career_stage_score("senior", "phd_student,postdoc")
    assert score == 0.0
    assert reason == "ineligible"


def test_career_stage_no_restriction():
    score, _ = _career_stage_score("senior", None)
    assert score == 1.0


def test_deadline_expired():
    score, reason = _deadline_score(date.today() - timedelta(days=1))
    assert score == 0.0
    assert "expired" in reason


def test_deadline_urgent():
    score, reason = _deadline_score(date.today() + timedelta(days=10))
    assert score == 1.0
    assert "urgent" in reason


def test_deadline_upcoming():
    score, _ = _deadline_score(date.today() + timedelta(days=60))
    assert abs(score - 0.7) < 0.01


def test_compute_match_score():
    # Create mock profile and opportunity with overlapping keywords
    profile = MagicMock()
    profile.keywords = [MagicMock(value="machine learning"), MagicMock(value="nlp")]
    profile.fields = [MagicMock(name="computer science")]
    profile.career_stage = MagicMock(value="postdoc")

    opp = MagicMock()
    opp.keywords = [MagicMock(value="machine learning"), MagicMock(value="deep learning")]
    opp.fields = [MagicMock(name="computer science")]
    opp.career_stages = "postdoc,early_career"
    opp.deadline = date.today() + timedelta(days=30)

    score, reasons = compute_match_score(profile, opp)
    assert 0.0 < score <= 1.0
    assert "keyword_overlap" in reasons
