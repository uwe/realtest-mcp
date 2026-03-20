import pytest
from pathlib import Path

from realtest_mcp.server import create_service
from tests.live_helpers import (
    build_live_service,
    invalid_live_script,
    load_fixture_script,
    require_live_settings,
)


@pytest.mark.live
def test_live_parse_invokes_realtest_and_creates_workspace() -> None:
    service = build_live_service()

    result = service.parse(invalid_live_script())

    assert result.command == "parse"
    assert result.script_path.endswith("script.rts")
    assert result.script_dir
    assert "timed out" not in (result.error or "").lower()
    if result.ok:
        assert result.error is None
    else:
        assert result.error


@pytest.mark.live
def test_live_parse_reports_errors_for_error_fixture() -> None:
    service = build_live_service()
    script = load_fixture_script("error.rts")

    result = service.parse(script)

    assert result.command == "parse"
    assert not result.ok
    assert result.script_path.endswith("script.rts")
    assert result.script_dir
    assert result.error
    assert "timed out" not in result.error.lower()


@pytest.mark.live
def test_live_service_factory_uses_real_subprocess_runner() -> None:
    settings = require_live_settings()

    service = create_service(settings)
    result = service.parse(invalid_live_script())

    assert result.command == "parse"
    assert "timed out" not in (result.error or "").lower()
    if result.ok:
        assert result.error is None
    else:
        assert result.error


@pytest.mark.live
def test_live_import_uses_simple_fixture() -> None:
    service = build_live_service()
    script = load_fixture_script("simple.rts")

    result = service.import_data(script)

    assert result.command == "import"
    assert result.ok, result.error or result.stderr
    assert result.error is None
    assert result.script_path.endswith("script.rts")
    assert result.script_dir


@pytest.mark.live
def test_live_optimize_uses_simple_fixture() -> None:
    service = build_live_service()
    script = load_fixture_script("simple.rts")

    result = service.optimize(script)

    assert result.command == "optimize"
    assert result.ok, result.error or result.stderr
    assert result.error is None
    assert result.stats_paths
    assert result.trades_paths

    stats_paths = [Path(path) for path in result.stats_paths]
    trades_paths = [Path(path) for path in result.trades_paths]

    for path in [*stats_paths, *trades_paths]:
        assert path.exists(), f"missing output file: {path}"
        assert path.stat().st_size > 0, f"empty output file: {path}"

    assert [path.name for path in stats_paths] == [
        "stats.1.csv",
        "stats.2.csv",
        "stats.3.csv",
        "stats.4.csv",
    ]
    assert [path.name for path in trades_paths] == [
        "trades.1.csv",
        "trades.2.csv",
        "trades.3.csv",
        "trades.4.csv",
    ]


@pytest.mark.live
def test_live_test_uses_simple_fixture_and_is_repeatable() -> None:
    service = build_live_service()
    script = load_fixture_script("simple.rts")

    first = service.test(script)
    second = service.test(script)

    assert first.command == "test"
    assert first.ok, first.error or first.stderr
    assert second.ok, second.error or second.stderr

    first_stats = Path(first.stats_path)
    first_trades = Path(first.trades_path)
    first_positions = Path(first.positions_path)
    second_stats = Path(second.stats_path)
    second_trades = Path(second.trades_path)
    second_positions = Path(second.positions_path)

    for path in [
        first_stats,
        first_trades,
        first_positions,
        second_stats,
        second_trades,
        second_positions,
    ]:
        assert path.exists(), f"missing output file: {path}"
        assert path.stat().st_size > 0, f"empty output file: {path}"

    assert first_stats.read_text(encoding="utf-8") == second_stats.read_text(
        encoding="utf-8"
    )
    assert first_trades.read_text(encoding="utf-8") == second_trades.read_text(
        encoding="utf-8"
    )
    assert first_positions.read_text(encoding="utf-8") == second_positions.read_text(
        encoding="utf-8"
    )
