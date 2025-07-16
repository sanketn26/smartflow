# Development Setup

## Prerequisites

- Python 3.9+
- Poetry (for dependency management)

## Setup

1. Clone the repository:
```bash
git clone https://github.com/sanketn26/smartflow.git
cd smartflow
```

2. Install dependencies:
```bash
poetry install
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run tests:
```bash
poetry run pytest
```

## Development Workflow

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=smartflow

# Run specific test file
poetry run pytest tests/test_storage.py

# Run with verbose output
poetry run pytest -v
```

### Code Formatting

```bash
# Format code with black
poetry run black smartflow/ tests/

# Sort imports with isort
poetry run isort smartflow/ tests/

# Run linting with flake8
poetry run flake8 smartflow/ tests/
```

### Type Checking

```bash
poetry run mypy smartflow/
```

### Running Examples

```bash
# Run the sentiment analysis example
poetry run python examples/sentiment_analysis.py

# Run with custom input
export LLM_PROVIDER=openai
export OPENAI_API_KEY=your_key
poetry run python examples/sentiment_analysis.py
```

### Building the Package

```bash
# Build the package
poetry build

# Install locally
pip install dist/smartflow-*.whl
```

## Project Structure

```
smartflow/
├── smartflow/              # Main package
│   ├── __init__.py
│   ├── workflow.py         # Workflow orchestration
│   ├── step.py            # Step implementation
│   ├── substep.py         # Substep implementation
│   ├── storage.py         # Storage backends
│   ├── config.py          # Configuration
│   ├── callbacks.py       # Callback handlers
│   ├── state.py           # State management
│   ├── dashboard.py       # Streamlit dashboard
│   ├── cli.py             # Command-line interface
│   └── utils.py           # Utility functions
├── tests/                 # Test suite
├── examples/              # Usage examples
├── docs/                  # Documentation
└── pyproject.toml         # Poetry configuration
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create a release tag
4. Build and publish to PyPI:
   ```bash
   poetry build
   poetry publish
   ```
