from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class Settings(BaseModel):
    model_config = ConfigDict(frozen=True)

    realtest_path: Path = Path("C:\\RealTest")
    script_path: Path
    script_digits: int = Field(ge=1)
    host: str = "0.0.0.0"
    port: int = Field(default=8000, ge=1024, le=65535)
    streamable_http_path: str = "/mcp"
    command_timeout_seconds: int | None = Field(default=30, ge=1)

    @property
    def realtest_executable(self) -> Path:
        return self.realtest_path / "RealTest.exe"

    @property
    def error_log_path(self) -> Path:
        return self.realtest_path / "errorlog.txt"

    @classmethod
    def from_env(
        cls,
        environ: dict[str, str] | None = None,
        *,
        env_file: Path | None = None,
    ) -> "Settings":
        env = cls._build_environment(environ=environ, env_file=env_file)
        data = {
            "realtest_path": env.get("REALTEST_MCP_REALTEST_PATH", "C:\\RealTest"),
            "script_path": env["REALTEST_MCP_SCRIPT_PATH"],
            "script_digits": env.get("REALTEST_MCP_SCRIPT_DIGITS", "4"),
            "host": env.get("REALTEST_MCP_HOST", "127.0.0.1"),
            "port": env.get("REALTEST_MCP_PORT", "8000"),
            "streamable_http_path": env.get(
                "REALTEST_MCP_STREAMABLE_HTTP_PATH", "/mcp"
            ),
            "command_timeout_seconds": env.get(
                "REALTEST_MCP_COMMAND_TIMEOUT_SECONDS", "30"
            ),
        }
        try:
            return cls.model_validate(data)
        except ValidationError as exc:
            raise ValueError(f"Invalid RealTest MCP settings: {exc}") from exc

    @classmethod
    def _build_environment(
        cls,
        environ: dict[str, str] | None,
        env_file: Path | None,
    ) -> dict[str, str]:
        if environ is not None:
            return dict(environ)

        merged = cls._read_dotenv(env_file or Path.cwd() / ".env")
        merged.update(os.environ)
        return merged

    @staticmethod
    def _read_dotenv(path: Path) -> dict[str, str]:
        if not path.exists():
            return {}

        values: dict[str, str] = {}
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
        return values
