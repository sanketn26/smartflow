.PHONY: help install test lint format type-check clean build docs setup

help:
	@echo "Available commands:"
	@echo "  setup      - Set up development environment"
	@echo "  install    - Install dependencies"
	@echo "  test       - Run tests"
	@echo "  test-cov   - Run tests with coverage"
	@echo "  lint       - Run linting"
	@echo "  format     - Format code"
	@echo "  type-check - Run type checking"
	@echo "  clean      - Clean build artifacts"
	@echo "  build      - Build package"
	@echo "  docs       - Build documentation"
	@echo "  example    - Run example workflow"

setup:
	python setup_dev.py

install:
	poetry install

test:
	poetry run pytest tests/ -v

test-cov:
	poetry run pytest tests/ --cov=smartflow --cov-report=html --cov-report=term

lint:
	poetry run flake8 smartflow/ tests/

format:
	poetry run black smartflow/ tests/
	poetry run isort smartflow/ tests/

type-check:
	poetry run mypy smartflow/

clean:
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:
	poetry build

docs:
	@echo "Documentation is in docs/ directory"
	@echo "For Streamlit dashboard: poetry run streamlit run smartflow/dashboard.py"

example:
	poetry run python examples/sentiment_analysis.py

# Development shortcuts
dev-setup: setup
dev-test: test-cov lint type-check
dev-format: format
dev-clean: clean
