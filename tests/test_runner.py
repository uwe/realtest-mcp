import subprocess
import tempfile
from pathlib import Path

from realtest_mcp.runner import ProcessResult, RealTestRunner, SubprocessRunner


class FakeCommandRunner:
    def __init__(self, result: ProcessResult) -> None:
        self.result = result
        self.calls = []

    def run(self, command: list[str], cwd: Path | None = None) -> ProcessResult:
        self.calls.append((command, cwd))
        return self.result


def test_builds_expected_cli_commands() -> None:
    runner = RealTestRunner(
        Path(r"C:\RealTest\RealTest.exe"), Path(r"C:\RealTest\errorlog.txt")
    )

    command = runner.build_command("parse", Path(r"Z:\mcp\script-0000\script.rts"))

    assert command == [
        r"C:\RealTest\RealTest.exe",
        "-parse",
        r"Z:\mcp\script-0000\script.rts",
    ]


def test_run_uses_command_runner_with_script_directory_as_cwd() -> None:
    fake = FakeCommandRunner(ProcessResult(returncode=0, stdout="ok"))
    script_path = Path(r"Z:\mcp\script-0000\script.rts")
    runner = RealTestRunner(
        Path(r"C:\RealTest\RealTest.exe"), Path(r"C:\RealTest\errorlog.txt"), fake
    )

    result = runner.run("import", script_path)

    assert result.stdout == "ok"
    assert fake.calls == [
        (
            [r"C:\RealTest\RealTest.exe", "-import", r"Z:\mcp\script-0000\script.rts"],
            Path(r"Z:\mcp\script-0000"),
        )
    ]


def test_build_command_supports_optimize() -> None:
    runner = RealTestRunner(
        Path(r"C:\RealTest\RealTest.exe"), Path(r"C:\RealTest\errorlog.txt")
    )

    command = runner.build_command("optimize", Path(r"Z:\mcp\script-0000\script.rts"))

    assert command == [
        r"C:\RealTest\RealTest.exe",
        "-optimize",
        r"Z:\mcp\script-0000\script.rts",
    ]


def test_reads_last_non_empty_error_line() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        error_log = Path(tmp_dir) / "errorlog.txt"
        error_log.write_text("first\n\nlast useful line\n", encoding="utf-8")
        runner = RealTestRunner(Path(r"C:\RealTest\RealTest.exe"), error_log)

        assert runner.read_last_error() == "last useful line"


def test_subprocess_runner_returns_timeout_result(monkeypatch) -> None:
    def fake_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(
            cmd=kwargs.get("args", args[0]), timeout=5, output="partial", stderr="slow"
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    runner = SubprocessRunner(timeout_seconds=5)
    result = runner.run(["RealTest.exe", "parse", "script.rts"])

    assert result.returncode == 124
    assert result.stdout == "partial"
    assert "timed out after 5 seconds" in result.stderr


def test_subprocess_runner_returns_completed_process_output(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_run(command, **kwargs):
        captured["command"] = command
        captured["cwd"] = kwargs.get("cwd")
        captured["timeout"] = kwargs.get("timeout")
        return subprocess.CompletedProcess(command, 0, stdout="done", stderr="warn")

    monkeypatch.setattr(subprocess, "run", fake_run)

    cwd = Path(r"Z:\mcp\script-0000")
    runner = SubprocessRunner(timeout_seconds=7)
    result = runner.run(["RealTest.exe", "-parse", "script.rts"], cwd=cwd)

    assert result == ProcessResult(returncode=0, stdout="done", stderr="warn")
    assert captured == {
        "command": ["RealTest.exe", "-parse", "script.rts"],
        "cwd": str(cwd),
        "timeout": 7,
    }


def test_read_last_error_returns_none_for_missing_or_blank_file() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = Path(tmp_dir)
        missing_runner = RealTestRunner(
            Path(r"C:\RealTest\RealTest.exe"), root / "missing.txt"
        )

        assert missing_runner.read_last_error() is None

        blank_log = root / "errorlog.txt"
        blank_log.write_text("\n   \n", encoding="utf-8")
        blank_runner = RealTestRunner(Path(r"C:\RealTest\RealTest.exe"), blank_log)

        assert blank_runner.read_last_error() is None
