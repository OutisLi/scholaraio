"""Contract tests for workspace management.

Verifies: create initializes workspace, read_paper_ids returns correct set,
internal consistency of papers.json is maintained.
Does NOT test: add/remove (requires index DB with lookup_paper).
"""

from __future__ import annotations

import json

from scholaraio.workspace import create, list_workspaces, read_paper_ids


class TestWorkspaceCreate:
    """Workspace creation contract."""

    def test_create_initializes_directory(self, tmp_path):
        ws_dir = tmp_path / "workspace" / "test-ws"
        create(ws_dir)
        assert ws_dir.is_dir()
        assert (ws_dir / "papers.json").exists()

    def test_create_idempotent(self, tmp_path):
        ws_dir = tmp_path / "workspace" / "test-ws"
        create(ws_dir)
        create(ws_dir)
        # Should not corrupt existing papers.json
        data = json.loads((ws_dir / "papers.json").read_text())
        assert data == []


class TestReadPaperIds:
    """read_paper_ids contract: returns set of UUIDs from papers.json."""

    def test_empty_workspace(self, tmp_path):
        ws_dir = tmp_path / "ws"
        create(ws_dir)
        assert read_paper_ids(ws_dir) == set()

    def test_reads_ids_from_papers_json(self, tmp_path):
        ws_dir = tmp_path / "ws"
        create(ws_dir)
        # Write entries directly to simulate add()
        entries = [
            {"id": "aaaa-1111", "dir_name": "Smith-2023-Test", "added_at": "2024-01-01"},
            {"id": "bbbb-2222", "dir_name": "Wang-2024-Test", "added_at": "2024-01-01"},
        ]
        (ws_dir / "papers.json").write_text(json.dumps(entries))

        ids = read_paper_ids(ws_dir)
        assert ids == {"aaaa-1111", "bbbb-2222"}

    def test_nonexistent_workspace_returns_empty(self, tmp_path):
        ids = read_paper_ids(tmp_path / "nonexistent")
        assert ids == set()


class TestListWorkspaces:
    """list_workspaces contract: discovers workspace directories."""

    def test_lists_created_workspaces(self, tmp_path):
        ws_root = tmp_path / "workspace"
        create(ws_root / "alpha")
        create(ws_root / "beta")

        names = list_workspaces(ws_root)
        assert set(names) == {"alpha", "beta"}

    def test_ignores_dirs_without_papers_json(self, tmp_path):
        ws_root = tmp_path / "workspace"
        create(ws_root / "real")
        (ws_root / "fake").mkdir(parents=True)

        names = list_workspaces(ws_root)
        assert names == ["real"]
