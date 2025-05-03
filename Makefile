.PHONY: format lint

format:
	uv run black .

lint:
	uv run ruff check --fix

all: format lint