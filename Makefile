.PHONY: install lint format check test clean build

## Install all dependencies (including dev)
install:
	uv sync --dev

## Run ruff linter
lint:
	uv run ruff check structflo/ tests/

## Auto-fix lint issues
fix:
	uv run ruff check --fix structflo/ tests/

## Format code with ruff
format:
	uv run ruff format structflo/ tests/

## Check formatting + lint (CI-friendly, no changes)
check:
	uv run ruff format --check structflo/ tests/
	uv run ruff check structflo/ tests/

## Run tests
test:
	uv run pytest -q

## Remove build artifacts
clean:
	rm -rf dist/ build/ *.egg-info .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} +

## Build package
build:
	uv build
