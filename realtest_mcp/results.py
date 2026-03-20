from __future__ import annotations

from pydantic import BaseModel, Field


class CommandResult(BaseModel):
    ok: bool
    command: str
    script_dir: str
    script_path: str
    stdout: str = ""
    stderr: str = ""
    error: str | None = None


class ParseResult(CommandResult):
    pass


class ImportResult(CommandResult):
    pass


class OptimizeResult(CommandResult):
    stats_paths: list[str] = Field(default_factory=list)
    trades_paths: list[str] = Field(default_factory=list)


class TestResult(CommandResult):
    stats_path: str
    trades_path: str
    positions_path: str
