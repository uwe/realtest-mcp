import tempfile
from pathlib import Path

from realtest_mcp.workspace import WorkspaceAllocator


def test_creates_next_script_directory_and_expected_files() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        (root / "script-0000").mkdir()

        allocator = WorkspaceAllocator(root, digits=4)
        workspace = allocator.create("Strategy: Test")

        assert workspace.directory.name == "script-0001"
        assert workspace.script_path.name == "script.rts"
        assert workspace.script_path.read_text(encoding="utf-8") == "Strategy: Test"
        assert workspace.stats_path.name == "stats.csv"
        assert workspace.trades_path.name == "trades.csv"
        assert workspace.positions_path.name == "positions.csv"


def test_next_index_ignores_non_matching_directories_and_files() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        (root / "script-0003").mkdir()
        (root / "script-xyz").mkdir()
        (root / "script-12").mkdir()
        (root / "notes.txt").write_text("ignored", encoding="utf-8")

        allocator = WorkspaceAllocator(root, digits=4)
        workspace = allocator.create("Strategy: Another")

        assert workspace.directory.name == "script-0004"


def test_create_makes_root_directory_when_missing() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir) / "nested" / "scripts"

        allocator = WorkspaceAllocator(root, digits=3)
        workspace = allocator.create("Strategy: Fresh")

        assert root.exists()
        assert workspace.directory.name == "script-000"
