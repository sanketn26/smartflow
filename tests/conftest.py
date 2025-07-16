"""
Pytest configuration and fixtures for SmartFlow tests.
"""

import os
import pytest
import tempfile
from unittest.mock import Mock

# Set test mode
os.environ["TEST_MODE"] = "true"


@pytest.fixture
def mock_llm():
    """Mock LLM for testing."""
    llm = Mock()
    llm.invoke = Mock(return_value="Mock LLM response")
    return llm


@pytest.fixture
def mock_embeddings():
    """Mock embeddings for testing."""
    embeddings = Mock()
    embeddings.embed_query = Mock(return_value=[0.1, 0.2, 0.3])
    return embeddings


@pytest.fixture
def temp_db_path():
    """Temporary database path for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    yield db_path
    try:
        os.unlink(db_path)
    except FileNotFoundError:
        pass


@pytest.fixture
def temp_json_files():
    """Temporary JSON files for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = os.path.join(tmpdir, "state.json")
        log_file = os.path.join(tmpdir, "logs.json")
        yield state_file, log_file


@pytest.fixture
def sample_input_data():
    """Sample input data for testing."""
    return {"input_data": "This is a test input for sentiment analysis."}


@pytest.fixture
def sample_success_criteria():
    """Sample success criteria for testing."""
    return {
        "min_quality_score": 0.8,
        "keywords": ["test", "analysis"],
        "output_format": "json",
        "goal": "Test goal"
    }
