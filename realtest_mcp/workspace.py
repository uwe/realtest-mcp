from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ScriptWorkspace:
    directory: Path
    script_path: Path
    stats_path: Path
    trades_path: Path
    positions_path: Path


class WorkspaceAllocator:
    def __init__(self, root: Path, digits: int) -> None:
        self.root = root
        self.digits = digits

    def create(self, script: str) -> ScriptWorkspace:
        self.root.mkdir(parents=True, exist_ok=True)
        index = self._next_index()
        directory = self.root / f"script-{index:0{self.digits}d}"
        directory.mkdir()
        script_path = directory / "script.rts"
        script_path.write_text(script, encoding="utf-8")
        return ScriptWorkspace(
            directory=directory,
            script_path=script_path,
            stats_path=directory / "stats.csv",
            trades_path=directory / "trades.csv",
            positions_path=directory / "positions.csv",
        )

    def _next_index(self) -> int:
        prefix = "script-"
        width = self.digits
        highest = -1
        for child in self.root.iterdir():
            if not child.is_dir() or not child.name.startswith(prefix):
                continue
            suffix = child.name[len(prefix) :]
            if len(suffix) != width or not suffix.isdigit():
                continue
            highest = max(highest, int(suffix))
        return highest + 1
