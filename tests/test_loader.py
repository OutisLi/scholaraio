"""Contract tests for the L1-L2 layer loading system.

Verifies: each layer returns the documented fields from well-formed data.
Does NOT test: internal JSON parsing details, LLM enrichment paths, or L3/L4
layers that require LLM enrichment or full-text paper files.
"""

from __future__ import annotations

import json

from scholaraio.loader import load_l1, load_l2


class TestLoadL1:
    """L1 contract: returns metadata dict with documented keys."""

    def test_returns_expected_keys(self, tmp_papers):
        json_path = tmp_papers / "Smith-2023-Turbulence" / "meta.json"
        result = load_l1(json_path)

        assert result["paper_id"] == "aaaa-1111"
        assert result["title"] == "Turbulence modeling in boundary layers"
        assert isinstance(result["authors"], list)
        assert result["year"] == 2023
        assert result["journal"] == "Journal of Fluid Mechanics"
        assert result["doi"] == "10.1234/jfm.2023.001"

    def test_missing_fields_have_safe_defaults(self, tmp_path):
        """Minimal JSON should not crash — missing fields get defaults."""
        d = tmp_path / "Bare-2000-Minimal"
        d.mkdir(parents=True)
        (d / "meta.json").write_text(json.dumps({"id": "min-id"}))

        result = load_l1(d / "meta.json")
        assert result["paper_id"] == "min-id"
        assert result["title"] == ""
        assert result["authors"] == []
        assert result["year"] is None


class TestLoadL2:
    """L2 contract: returns abstract string."""

    def test_returns_abstract(self, tmp_papers):
        json_path = tmp_papers / "Smith-2023-Turbulence" / "meta.json"
        assert "novel turbulence model" in load_l2(json_path)

    def test_missing_abstract_returns_placeholder(self, tmp_path):
        d = tmp_path / "NoAbstract"
        d.mkdir()
        (d / "meta.json").write_text(json.dumps({"id": "x"}))

        result = load_l2(d / "meta.json")
        assert "No abstract" in result
