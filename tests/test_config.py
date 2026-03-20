from pathlib import Path
import tempfile

import pytest

from realtest_mcp.config import Settings


def test_from_env_uses_localhost_http_defaults() -> None:
    settings = Settings.from_env(
        {
            "REALTEST_MCP_REALTEST_PATH": r"C:\RealTest",
            "REALTEST_MCP_SCRIPT_PATH": r"Z:\mcp",
        }
    )

    assert settings.host == "127.0.0.1"
    assert settings.port == 8000
    assert settings.streamable_http_path == "/mcp"
    assert settings.script_digits == 4
    assert settings.command_timeout_seconds == 30
    assert settings.realtest_executable == Path(r"C:\RealTest") / "RealTest.exe"
    assert settings.error_log_path == Path(r"C:\RealTest") / "errorlog.txt"


def test_from_env_reads_repo_dotenv_file() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        env_file = Path(tmp_dir) / ".env"
        env_file.write_text(
            "\n".join(
                [
                    r"REALTEST_MCP_REALTEST_PATH=C:\RealTest",
                    r"REALTEST_MCP_SCRIPT_PATH=Z:\mcp",
                    "REALTEST_MCP_SCRIPT_DIGITS=6",
                    "REALTEST_MCP_HOST=127.0.0.1",
                    "REALTEST_MCP_PORT=9001",
                    "REALTEST_MCP_STREAMABLE_HTTP_PATH=/custom-mcp",
                    "REALTEST_MCP_COMMAND_TIMEOUT_SECONDS=12",
                ]
            ),
            encoding="utf-8",
        )

        settings = Settings.from_env(env_file=env_file)

        assert settings.realtest_path == Path(r"C:\RealTest")
        assert settings.script_path == Path(r"Z:\mcp")
        assert settings.script_digits == 6
        assert settings.host == "127.0.0.1"
        assert settings.port == 9001
        assert settings.streamable_http_path == "/custom-mcp"
        assert settings.command_timeout_seconds == 12


def test_from_env_prefers_explicit_environment_over_dotenv() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        env_file = Path(tmp_dir) / ".env"
        env_file.write_text(
            "\n".join(
                [
                    r"REALTEST_MCP_REALTEST_PATH=C:\FromDotEnv",
                    r"REALTEST_MCP_SCRIPT_PATH=Z:\dotenv",
                    "REALTEST_MCP_HOST=127.0.0.1",
                ]
            ),
            encoding="utf-8",
        )

        settings = Settings.from_env(
            {
                "REALTEST_MCP_REALTEST_PATH": r"C:\FromEnv",
                "REALTEST_MCP_SCRIPT_PATH": r"Z:\explicit",
                "REALTEST_MCP_HOST": "0.0.0.0",
            },
            env_file=env_file,
        )

        assert settings.realtest_path == Path(r"C:\FromEnv")
        assert settings.script_path == Path(r"Z:\explicit")
        assert settings.host == "0.0.0.0"


def test_read_dotenv_ignores_comments_invalid_lines_and_strips_quotes() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        env_file = Path(tmp_dir) / ".env"
        env_file.write_text(
            "\n".join(
                [
                    "# comment",
                    "MALFORMED_LINE",
                    "REALTEST_MCP_SCRIPT_PATH='Z:\\quoted'",
                    'REALTEST_MCP_STREAMABLE_HTTP_PATH="/quoted-path"',
                ]
            ),
            encoding="utf-8",
        )

        values = Settings._read_dotenv(env_file)

        assert values == {
            "REALTEST_MCP_SCRIPT_PATH": r"Z:\quoted",
            "REALTEST_MCP_STREAMABLE_HTTP_PATH": "/quoted-path",
        }


def test_from_env_rejects_invalid_values() -> None:
    with pytest.raises(ValueError, match="Invalid RealTest MCP settings"):
        Settings.from_env(
            {
                "REALTEST_MCP_REALTEST_PATH": r"C:\RealTest",
                "REALTEST_MCP_SCRIPT_PATH": r"Z:\mcp",
                "REALTEST_MCP_PORT": "80",
            }
        )
