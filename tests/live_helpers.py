from __future__ import annotations

from pathlib import Path

import pytest

from realtest_mcp.config import Settings
from realtest_mcp.runner import RealTestRunner
from realtest_mcp.service import RealTestService
from realtest_mcp.workspace import WorkspaceAllocator


LIVE_ENV_VAR = "REALTEST_MCP_RUN_LIVE_TESTS"
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def require_live_settings() -> Settings:
    env = Settings._build_environment(environ=None, env_file=None)
    if env.get(LIVE_ENV_VAR) != "1":
        pytest.skip(f"set {LIVE_ENV_VAR}=1 to run live RealTest tests")

    try:
        settings = Settings.from_env()
    except Exception as exc:
        pytest.skip(f"live settings are not available: {exc}")

    if not settings.realtest_executable.exists():
        pytest.skip(f"RealTest executable not found at {settings.realtest_executable}")

    settings.script_path.mkdir(parents=True, exist_ok=True)
    return settings


def build_live_service() -> RealTestService:
    settings = require_live_settings()
    allocator = WorkspaceAllocator(settings.script_path, settings.script_digits)
    runner = RealTestRunner(settings.realtest_executable, settings.error_log_path)
    return RealTestService(allocator, runner)


def invalid_live_script() -> str:
    return "This is not a valid RealTest script."


def load_fixture_script(name: str) -> str:
    return (FIXTURES_DIR / name).read_text(encoding="utf-8")
