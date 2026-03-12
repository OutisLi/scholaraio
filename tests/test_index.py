"""Contract tests for the FTS5 search index.

Verifies: build_index creates a searchable database, search returns
matching results with expected structure.
Does NOT test: SQLite internals, exact ranking scores, hash logic.
"""

from __future__ import annotations

from scholaraio.index import build_index, search


class TestBuildAndSearch:
    """End-to-end index contract: build → search → results."""

    def test_build_then_search_by_title(self, tmp_papers, tmp_db):
        build_index(tmp_papers, tmp_db)
        results = search("turbulence", tmp_db)
        assert len(results) >= 1
        titles = [r["title"] for r in results]
        assert any("Turbulence" in t or "turbulence" in t for t in titles)

    def test_search_returns_expected_fields(self, tmp_papers, tmp_db):
        build_index(tmp_papers, tmp_db)
        results = search("turbulence", tmp_db)
        assert len(results) >= 1
        r = results[0]
        # Contract: search results contain at minimum these keys
        for key in ("paper_id", "title", "authors", "year", "journal"):
            assert key in r, f"Missing key: {key}"

    def test_search_no_match_returns_empty(self, tmp_papers, tmp_db):
        build_index(tmp_papers, tmp_db)
        results = search("xyznonexistent", tmp_db)
        assert results == []

    def test_search_by_abstract_content(self, tmp_papers, tmp_db):
        build_index(tmp_papers, tmp_db)
        results = search("novel turbulence model boundary", tmp_db)
        assert len(results) >= 1

    def test_rebuild_is_idempotent(self, tmp_papers, tmp_db):
        """Building twice should not duplicate entries."""
        build_index(tmp_papers, tmp_db)
        build_index(tmp_papers, tmp_db)
        results = search("turbulence", tmp_db)
        # Should still find exactly one match for this query, not duplicates
        turbulence_results = [r for r in results if "Turbulence" in r.get("title", "")]
        assert len(turbulence_results) == 1
