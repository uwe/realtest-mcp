from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class ProcessResult:
    returncode: int
    stdout: str = ""
    stderr: str = ""


class CommandRunner(Protocol):
    def run(self, command: list[str], cwd: Path | None = None) -> ProcessResult: ...


class SubprocessRunner:
    def __init__(self, timeout_seconds: int | None = None) -> None:
        self.timeout_seconds = timeout_seconds

    def run(self, command: list[str], cwd: Path | None = None) -> ProcessResult:
        try:
            completed = subprocess.run(
                command,
                cwd=str(cwd) if cwd else None,
                capture_output=True,
                text=True,
                check=False,
                timeout=self.timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            return ProcessResult(
                returncode=124,
                stdout=exc.stdout or "",
                stderr=(exc.stderr or "")
                + f"RealTest command timed out after {self.timeout_seconds} seconds",
            )
        return ProcessResult(
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )


class RealTestRunner:
    def __init__(
        self,
        executable: Path,
        error_log_path: Path,
        command_runner: CommandRunner | None = None,
        timeout_seconds: int | None = None,
    ) -> None:
        self.executable = executable
        self.error_log_path = error_log_path
        self.command_runner = command_runner or SubprocessRunner(
            timeout_seconds=timeout_seconds
        )

    def run(self, command_name: str, script_path: Path) -> ProcessResult:
        command = self.build_command(command_name, script_path)
        return self.command_runner.run(command, cwd=script_path.parent)

    def build_command(self, command_name: str, script_path: Path) -> list[str]:
        return [str(self.executable), f"-{command_name}", str(script_path)]

    def read_last_error(self) -> str | None:
        if not self.error_log_path.exists():
            return None
        lines = self.error_log_path.read_text(encoding="utf-8").splitlines()
        for line in reversed(lines):
            if line.strip():
                return line.strip()
        return None
