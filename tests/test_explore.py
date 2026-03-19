"""Tests for explore filter construction and name validation."""

from __future__ import annotations

from scholaraio.explore import _build_filter


class TestBuildFilter:
    def test_min_citations_positive_adds_filter(self):
        filt, _ = _build_filter(min_citations=10)
        assert "cited_by_count:>9" in filt

    def test_min_citations_zero_or_negative_ignored(self):
        filt_zero, _ = _build_filter(min_citations=0)
        filt_negative, _ = _build_filter(min_citations=-3)
        assert "cited_by_count" not in filt_zero
        assert "cited_by_count" not in filt_negative
