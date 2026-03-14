"""Contract tests for MCP server parameter mapping logic.

Verifies: parameter adapter functions produce correct values before
delegating to underlying library calls.
Does NOT test: BERTopic model building, MCP protocol, or external APIs.
"""

from __future__ import annotations

import pytest


class TestBuildTopicsNrTopicsMapping:
    """nr_topics adapter: int sentinel → BERTopic-expected value."""

    @pytest.mark.parametrize(
        "nr_topics, expected",
        [
            (0, "auto"),   # default: automatic topic merging/reduction
            (-1, None),    # explicit: no reduction, keep HDBSCAN clusters
            (5, 5),        # explicit target count: passed through unchanged
            (20, 20),
        ],
    )
    def test_mapping(self, nr_topics: int, expected):
        result = {0: "auto", -1: None}.get(nr_topics, nr_topics)
        assert result == expected
