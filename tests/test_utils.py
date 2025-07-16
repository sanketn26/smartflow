"""
Tests for SmartFlow utilities.
"""

import pytest
from smartflow.utils import (
    sample_python_function,
    sample_data_processor,
    sample_validation_function,
    create_mock_documents,
    extract_sentiment_keywords,
    create_default_success_criteria
)


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_sample_python_function(self):
        """Test sample Python function."""
        inputs = {"input_data": "hello world"}
        result = sample_python_function(inputs)
        
        assert "result" in result
        assert result["result"] == "Processed by Python: HELLO WORLD"
        
        # Test with empty input
        empty_inputs = {}
        result = sample_python_function(empty_inputs)
        assert result["result"] == "Processed by Python: "
    
    def test_sample_data_processor(self):
        """Test sample data processor."""
        inputs = {"input_data": "  Hello World  "}
        result = sample_data_processor(inputs)
        
        assert "result" in result
        assert isinstance(result["result"], dict)
        
        output = result["result"]
        assert output["processed_text"] == "hello world"
        assert output["word_count"] == 2
        assert output["char_count"] == 11
        assert "summary" in output
    
    def test_sample_validation_function(self):
        """Test sample validation function."""
        # Test valid input
        valid_inputs = {"input_data": "valid text"}
        result = sample_validation_function(valid_inputs)
        
        assert "result" in result
        output = result["result"]
        assert output["is_valid"] is True
        assert len(output["errors"]) == 0
        assert "passed" in output["message"]
        
        # Test empty input
        empty_inputs = {"input_data": ""}
        result = sample_validation_function(empty_inputs)
        
        output = result["result"]
        assert output["is_valid"] is False
        assert len(output["errors"]) > 0
        assert "failed" in output["message"]
        
        # Test whitespace input
        whitespace_inputs = {"input_data": "   "}
        result = sample_validation_function(whitespace_inputs)
        
        output = result["result"]
        assert output["is_valid"] is False
        assert len(output["errors"]) > 0
    
    def test_create_mock_documents(self):
        """Test mock document creation."""
        documents = create_mock_documents()
        
        assert isinstance(documents, list)
        assert len(documents) > 0
        assert all(isinstance(doc, str) for doc in documents)
        assert any("SmartFlow" in doc for doc in documents)
    
    def test_extract_sentiment_keywords(self):
        """Test sentiment keyword extraction."""
        keywords = extract_sentiment_keywords()
        
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        assert "positive" in keywords
        assert "negative" in keywords
        assert "sentiment" in keywords
    
    def test_create_default_success_criteria(self):
        """Test default success criteria creation."""
        criteria = create_default_success_criteria()
        
        assert isinstance(criteria, dict)
        assert "min_quality_score" in criteria
        assert "max_retries" in criteria
        assert "timeout" in criteria
        assert "required_keys" in criteria
        assert "evaluation_explanation" in criteria
        
        # Check default values
        assert criteria["min_quality_score"] == 0.7
        assert criteria["max_retries"] == 3
        assert criteria["timeout"] == 30
        assert "result" in criteria["required_keys"]
