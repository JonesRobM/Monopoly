.PHONY: help install install-dev test test-cov test-fast lint format clean docs

help:  ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install package with core dependencies
	pip install -e .

install-dev:  ## Install package with development dependencies
	pip install -e ".[dev]"

install-all:  ## Install package with all dependencies
	pip install -e ".[all]"

test:  ## Run all tests
	pytest

test-cov:  ## Run tests with coverage report
	pytest --cov=engine --cov=env --cov-report=term-missing --cov-report=html

test-fast:  ## Run tests in parallel (fast)
	pytest -n auto

test-unit:  ## Run unit tests only
	pytest -m "not integration"

test-integration:  ## Run integration tests only
	pytest -m integration

lint:  ## Run linting checks (ruff, mypy)
	@echo "Running ruff..."
	ruff check engine env
	@echo "Running mypy..."
	mypy engine env

format:  ## Format code with black and ruff
	@echo "Running black..."
	black engine env
	@echo "Running ruff fix..."
	ruff check --fix engine env

format-check:  ## Check code formatting without modifying files
	black --check engine env
	ruff check engine env

type-check:  ## Run type checking with mypy
	mypy engine env

clean:  ## Clean build artifacts and caches
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

example:  ## Run example usage script
	python example_usage.py

shell:  ## Start interactive Python shell with imports
	python -i -c "from engine import *; from env import *; print('Monopoly AI environment loaded')"

# For Windows users, use these targets instead:
clean-windows:  ## Clean build artifacts (Windows)
	if exist build rmdir /s /q build
	if exist dist rmdir /s /q dist
	if exist *.egg-info rmdir /s /q *.egg-info
	if exist .pytest_cache rmdir /s /q .pytest_cache
	if exist .mypy_cache rmdir /s /q .mypy_cache
	if exist .ruff_cache rmdir /s /q .ruff_cache
	if exist htmlcov rmdir /s /q htmlcov
	if exist .coverage del .coverage
	for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
	del /s /q *.pyc 2>nul
	del /s /q *.pyo 2>nul
