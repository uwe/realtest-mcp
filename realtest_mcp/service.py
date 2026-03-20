from __future__ import annotations

from realtest_mcp.results import ImportResult, OptimizeResult, ParseResult, TestResult
from realtest_mcp.runner import RealTestRunner
from realtest_mcp.workspace import WorkspaceAllocator


class RealTestService:
    def __init__(
        self, workspace_allocator: WorkspaceAllocator, runner: RealTestRunner
    ) -> None:
        self.workspace_allocator = workspace_allocator
        self.runner = runner

    def parse(self, script: str) -> ParseResult:
        workspace = self.workspace_allocator.create(script)
        result = self.runner.run("parse", workspace.script_path)
        return ParseResult(
            ok=result.returncode == 0,
            command="parse",
            script_dir=str(workspace.directory),
            script_path=str(workspace.script_path),
            stdout=result.stdout,
            stderr=result.stderr,
            error=self._build_error(result),
        )

    def import_data(self, script: str) -> ImportResult:
        workspace = self.workspace_allocator.create(script)
        result = self.runner.run("import", workspace.script_path)
        return ImportResult(
            ok=result.returncode == 0,
            command="import",
            script_dir=str(workspace.directory),
            script_path=str(workspace.script_path),
            stdout=result.stdout,
            stderr=result.stderr,
            error=self._build_error(result),
        )

    def optimize(self, script: str) -> OptimizeResult:
        workspace = self.workspace_allocator.create(script)
        result = self.runner.run("optimize", workspace.script_path)
        return OptimizeResult(
            ok=result.returncode == 0,
            command="optimize",
            script_dir=str(workspace.directory),
            script_path=str(workspace.script_path),
            stdout=result.stdout,
            stderr=result.stderr,
            error=self._build_error(result),
        )

    def test(self, script: str) -> TestResult:
        workspace = self.workspace_allocator.create(script)
        result = self.runner.run("test", workspace.script_path)
        return TestResult(
            ok=result.returncode == 0,
            command="test",
            script_dir=str(workspace.directory),
            script_path=str(workspace.script_path),
            stdout=result.stdout,
            stderr=result.stderr,
            error=self._build_error(result),
            stats_path=str(workspace.stats_path),
            trades_path=str(workspace.trades_path),
            positions_path=str(workspace.positions_path),
        )

    def _build_error(self, result) -> str | None:
        if result.returncode == 0:
            return None
        return (
            self.runner.read_last_error()
            or result.stderr.strip()
            or "RealTest command failed"
        )
