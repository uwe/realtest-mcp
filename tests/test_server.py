import asyncio
import tempfile
from pathlib import Path
from unittest.mock import patch

from starlette.applications import Starlette

from realtest_mcp.config import Settings
from realtest_mcp.results import (
    ImportResult,
    OptimizeResult,
    ParseResult,
    TestResult as BacktestResult,
)
from realtest_mcp.server import create_app, create_service, main
from realtest_mcp.service import RealTestService
from realtest_mcp.workspace import WorkspaceAllocator


class FakeService:
    def parse(self, script: str) -> ParseResult:
        return ParseResult(
            ok=True,
            command="parse",
            script_dir="dir",
            script_path="file",
            stdout=script,
            stderr="",
        )

    def import_data(self, script: str) -> ImportResult:
        return ImportResult(
            ok=True,
            command="import",
            script_dir="dir",
            script_path="file",
            stdout=script,
            stderr="",
        )

    def optimize(self, script: str) -> OptimizeResult:
        return OptimizeResult(
            ok=True,
            command="optimize",
            script_dir="dir",
            script_path="file",
            stdout=script,
            stderr="",
        )

    def test(self, script: str) -> BacktestResult:
        return BacktestResult(
            ok=True,
            command="test",
            script_dir="dir",
            script_path="file",
            stdout=script,
            stderr="",
            stats_path="stats.csv",
            trades_path="trades.csv",
            positions_path="positions.csv",
        )


def test_create_app_registers_expected_tools_and_http_settings() -> None:
    settings = Settings(
        realtest_path=Path(r"C:\RealTest"),
        script_path=Path(r"Z:\mcp"),
        script_digits=4,
        host="0.0.0.0",
        port=9000,
        streamable_http_path="/mcp",
    )
    app = create_app(settings=settings, service=FakeService())

    tool_names = [tool.name for tool in asyncio.run(app.list_tools())]

    assert tool_names == ["parse", "import", "optimize", "test"]
    assert app.settings.host == "0.0.0.0"
    assert app.settings.port == 9000
    assert app.settings.streamable_http_path == "/mcp"


def test_tool_schema_requires_script_string() -> None:
    settings = Settings(
        realtest_path=Path(r"C:\RealTest"),
        script_path=Path(r"Z:\mcp"),
        script_digits=4,
    )
    app = create_app(settings=settings, service=FakeService())

    parse_tool = app._tool_manager.get_tool("parse")
    optimize_tool = app._tool_manager.get_tool("optimize")

    assert parse_tool is not None
    assert parse_tool.parameters["required"] == ["script"]
    assert parse_tool.parameters["properties"]["script"]["type"] == "string"
    assert optimize_tool is not None
    assert optimize_tool.parameters["required"] == ["script"]
    assert optimize_tool.parameters["properties"]["script"]["type"] == "string"


def test_registered_tools_delegate_to_service() -> None:
    settings = Settings(
        realtest_path=Path(r"C:\RealTest"),
        script_path=Path(r"Z:\mcp"),
        script_digits=4,
    )
    app = create_app(settings=settings, service=FakeService())

    parse_result = asyncio.run(app.call_tool("parse", {"script": "parse body"}))
    import_result = asyncio.run(app.call_tool("import", {"script": "import body"}))
    optimize_result = asyncio.run(
        app.call_tool("optimize", {"script": "optimize body"})
    )
    test_result = asyncio.run(app.call_tool("test", {"script": "test body"}))

    assert '"command": "parse"' in parse_result[0].text
    assert '"stdout": "parse body"' in parse_result[0].text
    assert '"command": "import"' in import_result[0].text
    assert '"stdout": "import body"' in import_result[0].text
    assert '"command": "optimize"' in optimize_result[0].text
    assert '"stdout": "optimize body"' in optimize_result[0].text
    assert '"command": "test"' in test_result[0].text
    assert '"stats_path": "stats.csv"' in test_result[0].text


def test_streamable_http_app_can_be_created() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        settings = Settings(
            realtest_path=Path(tmp_dir),
            script_path=Path(tmp_dir),
            script_digits=4,
        )
        app = create_app(settings=settings, service=FakeService())

        asgi_app = app.streamable_http_app()

        assert isinstance(asgi_app, Starlette)


def test_create_service_wires_workspace_allocator_and_runner_from_settings() -> None:
    settings = Settings(
        realtest_path=Path(r"C:\RealTest"),
        script_path=Path(r"Z:\mcp"),
        script_digits=6,
        command_timeout_seconds=45,
    )

    service = create_service(settings)

    assert isinstance(service, RealTestService)
    assert isinstance(service.workspace_allocator, WorkspaceAllocator)
    assert service.workspace_allocator.root == Path(r"Z:\mcp")
    assert service.workspace_allocator.digits == 6
    assert service.runner.executable == Path(r"C:\RealTest\RealTest.exe")
    assert service.runner.error_log_path == Path(r"C:\RealTest\errorlog.txt")
    assert service.runner.command_runner.timeout_seconds == 45


def test_create_app_uses_settings_from_env_when_not_provided() -> None:
    settings = Settings(
        realtest_path=Path(r"C:\RealTest"),
        script_path=Path(r"Z:\mcp"),
        script_digits=4,
        host="127.0.0.1",
        port=8123,
        streamable_http_path="/custom",
    )

    with patch("realtest_mcp.server.Settings.from_env", return_value=settings):
        app = create_app(service=FakeService())

    assert app.settings.host == "127.0.0.1"
    assert app.settings.port == 8123
    assert app.settings.streamable_http_path == "/custom"


def test_main_runs_streamable_http_transport() -> None:
    class FakeApp:
        def __init__(self) -> None:
            self.transport = None

        def run(self, transport: str) -> None:
            self.transport = transport

    fake_app = FakeApp()

    with patch("realtest_mcp.server.create_app", return_value=fake_app):
        main()

    assert fake_app.transport == "streamable-http"
