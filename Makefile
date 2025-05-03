.PHONY: format lint

format:
	uv run black .

lint:
	uv run ruff check --fix

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +

all: clean format lint