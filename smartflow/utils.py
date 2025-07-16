"""
Utility functions for SmartFlow.

This module contains helper functions and example implementations.
"""

import requests
from typing import Dict


def sample_python_function(inputs: Dict) -> Dict:
    """Example Python function for non-LLM substeps."""
    input_text = inputs.get("input_data", "")
    return {"result": f"Processed by Python: {input_text.upper()}"}


def sample_api_call(inputs: Dict) -> Dict:
    """Example API call function for non-LLM substeps."""
    try:
        response = requests.get(
            "https://api.example.com/data",
            params={"query": inputs.get("input_data", "")}
        )
        return {"result": response.json()}
    except Exception as e:
        return {"result": f"API call failed: {str(e)}"}


def sample_web_search(inputs: Dict) -> Dict:
    """Example web search function for non-LLM substeps."""
    query = inputs.get("input_data", "")
    return {"result": f"Web search results for {query}"}


def sample_data_processor(inputs: Dict) -> Dict:
    """Example data processing function."""
    data = inputs.get("input_data", "")
    
    # Simple text processing
    processed = data.strip().lower()
    word_count = len(processed.split())
    char_count = len(processed)
    
    return {
        "result": {
            "processed_text": processed,
            "word_count": word_count,
            "char_count": char_count,
            "summary": f"Processed {word_count} words and {char_count} characters"
        }
    }


def sample_validation_function(inputs: Dict) -> Dict:
    """Example validation function."""
    data = inputs.get("input_data", "")
    
    # Basic validation checks
    is_valid = bool(data and len(data.strip()) > 0)
    errors = []
    
    if not data:
        errors.append("Input data is empty")
    elif len(data.strip()) == 0:
        errors.append("Input data contains only whitespace")
    
    return {
        "result": {
            "is_valid": is_valid,
            "errors": errors,
            "message": "Validation passed" if is_valid else "Validation failed"
        }
    }


def create_mock_documents() -> list:
    """Create mock documents for RAG testing."""
    return [
        "SmartFlow is a modular AI workflow engine that supports various LLM providers.",
        "The system includes features like RAG, token tracking, and quality evaluation.",
        "Workflows consist of steps, which contain substeps that can be LLM or non-LLM tasks.",
        "The framework supports AWS Bedrock, OpenAI, and Ollama as LLM providers.",
        "Storage backends include SQLite and JSON file storage for state persistence.",
        "Quality evaluation includes automatic scoring and custom evaluation prompts.",
        "The dashboard provides observability with metrics, logs, and step details.",
        "Substeps can use past outputs for context and similarity-based relevance scoring."
    ]


def extract_sentiment_keywords() -> list:
    """Get common sentiment analysis keywords."""
    return [
        "positive", "negative", "neutral", "sentiment", "emotion",
        "happy", "sad", "angry", "excited", "disappointed",
        "confidence", "score", "analysis", "classification"
    ]


def create_default_success_criteria() -> Dict:
    """Create default success criteria for substeps."""
    return {
        "min_quality_score": 0.7,
        "max_retries": 3,
        "timeout": 30,
        "required_keys": ["result"],
        "evaluation_explanation": "Basic quality check passed"
    }
