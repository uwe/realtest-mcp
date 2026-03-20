import tempfile
from pathlib import Path

from realtest_mcp.runner import ProcessResult, RealTestRunner
from realtest_mcp.service import RealTestService
from realtest_mcp.workspace import WorkspaceAllocator


class FakeCommandRunner:
    def __init__(self, results: list[ProcessResult]) -> None:
        self.results = list(results)

    def run(self, command: list[str], cwd: Path | None = None) -> ProcessResult:
        return self.results.pop(0)


class WritingFakeCommandRunner:
    def __init__(self, result: ProcessResult) -> None:
        self.result = result

    def run(self, command: list[str], cwd: Path | None = None) -> ProcessResult:
        assert cwd is not None
        (cwd / "stats.2.csv").write_text("stats2", encoding="utf-8")
        (cwd / "stats.1.csv").write_text("stats1", encoding="utf-8")
        (cwd / "trades.2.csv").write_text("trades2", encoding="utf-8")
        (cwd / "trades.1.csv").write_text("trades1", encoding="utf-8")
        (cwd / "positions.1.csv").write_text("ignored", encoding="utf-8")
        return self.result


def test_parse_returns_failure_with_error_log_message() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        error_log = root / "errorlog.txt"
        error_log.write_text("ignored\nparse failed\n", encoding="utf-8")
        service = RealTestService(
            WorkspaceAllocator(root / "scripts", 4),
            RealTestRunner(
                Path(r"C:\RealTest\RealTest.exe"),
                error_log,
                FakeCommandRunner(
                    [ProcessResult(returncode=1, stderr="stderr message")]
                ),
            ),
        )

        result = service.parse("script body")

        assert not result.ok
        assert result.command == "parse"
        assert result.error == "parse failed"
        assert "stats_path" not in result.model_dump()


def test_import_returns_success_workspace_metadata() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        service = RealTestService(
            WorkspaceAllocator(root / "scripts", 4),
            RealTestRunner(
                Path(r"C:\RealTest\RealTest.exe"),
                root / "errorlog.txt",
                FakeCommandRunner([ProcessResult(returncode=0, stdout="imported")]),
            ),
        )

        result = service.import_data("script body")

        assert result.ok
        assert result.command == "import"
        assert result.script_path.endswith("script.rts")
        assert result.error is None


def test_optimize_returns_success_workspace_metadata() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        service = RealTestService(
            WorkspaceAllocator(root / "scripts", 4),
            RealTestRunner(
                Path(r"C:\RealTest\RealTest.exe"),
                root / "errorlog.txt",
                FakeCommandRunner([ProcessResult(returncode=0, stdout="optimized")]),
            ),
        )

        result = service.optimize("script body")

        assert result.ok
        assert result.command == "optimize"
        assert result.script_path.endswith("script.rts")
        assert result.error is None
        assert result.stats_paths == []
        assert result.trades_paths == []


def test_optimize_returns_parameterized_output_paths() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        service = RealTestService(
            WorkspaceAllocator(root / "scripts", 4),
            RealTestRunner(
                Path(r"C:\RealTest\RealTest.exe"),
                root / "errorlog.txt",
                WritingFakeCommandRunner(ProcessResult(returncode=0, stdout="optimized")),
            ),
        )

        result = service.optimize("script body")

        assert result.stats_paths == [
            str(Path(result.script_dir) / "stats.1.csv"),
            str(Path(result.script_dir) / "stats.2.csv"),
        ]
        assert result.trades_paths == [
            str(Path(result.script_dir) / "trades.1.csv"),
            str(Path(result.script_dir) / "trades.2.csv"),
        ]


def test_test_returns_csv_paths() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        service = RealTestService(
            WorkspaceAllocator(root / "scripts", 4),
            RealTestRunner(
                Path(r"C:\RealTest\RealTest.exe"),
                root / "errorlog.txt",
                FakeCommandRunner([ProcessResult(returncode=0, stdout="done")]),
            ),
        )

        result = service.test("script body")

        assert result.ok
        assert result.command == "test"
        assert result.stats_path.endswith("stats.csv")
        assert result.trades_path.endswith("trades.csv")
        assert result.positions_path.endswith("positions.csv")


def test_failure_falls_back_to_stderr_when_error_log_missing() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        service = RealTestService(
            WorkspaceAllocator(root / "scripts", 4),
            RealTestRunner(
                Path(r"C:\RealTest\RealTest.exe"),
                root / "missing-errorlog.txt",
                FakeCommandRunner(
                    [ProcessResult(returncode=1, stderr="runner stderr")]
                ),
            ),
        )

        result = service.import_data("script body")

        assert result.error == "runner stderr"


def test_failure_falls_back_to_generic_message_when_no_error_details_exist() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        service = RealTestService(
            WorkspaceAllocator(root / "scripts", 4),
            RealTestRunner(
                Path(r"C:\RealTest\RealTest.exe"),
                root / "missing-errorlog.txt",
                FakeCommandRunner([ProcessResult(returncode=1, stderr="   ")]),
            ),
        )

        result = service.optimize("script body")

        assert result.error == "RealTest command failed"
