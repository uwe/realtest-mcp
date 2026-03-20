from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from realtest_mcp.config import Settings
from realtest_mcp.runner import RealTestRunner
from realtest_mcp.service import RealTestService
from realtest_mcp.workspace import WorkspaceAllocator


def create_service(settings: Settings) -> RealTestService:
    allocator = WorkspaceAllocator(settings.script_path, settings.script_digits)
    runner = RealTestRunner(
        settings.realtest_executable,
        settings.error_log_path,
        timeout_seconds=settings.command_timeout_seconds,
    )
    return RealTestService(allocator, runner)


def create_app(
    settings: Settings | None = None, service: RealTestService | None = None
) -> FastMCP:
    settings = settings or Settings.from_env()
    service = service or create_service(settings)

    app = FastMCP(
        name="realtest-mcp",
        instructions="MCP server for RealTest backtesting operations.",
        host=settings.host,
        port=settings.port,
        streamable_http_path=settings.streamable_http_path,
    )

    @app.tool(name="parse", description="Validate a RealTest script for syntax errors.")
    def parse(script: str):
        return service.parse(script)

    @app.tool(name="import", description="Import data required by a RealTest script.")
    def import_data(script: str):
        return service.import_data(script)

    @app.tool(name="optimize", description="Run a RealTest optimization for a script.")
    def optimize(script: str):
        return service.optimize(script)

    @app.tool(name="test", description="Run a RealTest backtest script.")
    def test(script: str):
        return service.test(script)

    return app


def main() -> None:
    app = create_app()
    app.run(transport="streamable-http")
