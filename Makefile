test:
	uv run pytest

test-cov:
	uv run pytest --cov=realtest_mcp --cov-report=term-missing

live:
	uv run pytest -m live -rs
