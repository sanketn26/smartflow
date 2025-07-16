"""
Tests for SmartFlow storage backends.
"""

import json
import os
import tempfile
import pytest
from datetime import datetime

from smartflow.storage import SQLiteStorageBackend, JSONStorageBackend


class TestSQLiteStorageBackend:
    """Test SQLite storage backend."""
    
    def test_init_and_db_creation(self):
        """Test database initialization."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            backend = SQLiteStorageBackend(db_path=db_path)
            assert os.path.exists(db_path)
        finally:
            os.unlink(db_path)
    
    def test_save_and_load_state(self):
        """Test saving and loading workflow state."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            backend = SQLiteStorageBackend(db_path=db_path)
            
            # Test data
            workflow_id = "test_workflow"
            state_data = {"key": "value", "step1": {"result": "test"}}
            version = 1
            
            # Save state
            backend.save_state(workflow_id, state_data, version)
            
            # Load state
            loaded_state = backend.load_state(workflow_id)
            assert loaded_state == state_data
            
            # Test non-existent workflow
            empty_state = backend.load_state("non_existent")
            assert empty_state == {}
            
        finally:
            os.unlink(db_path)
    
    def test_log_step_and_get_logs(self):
        """Test logging steps and retrieving logs."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            backend = SQLiteStorageBackend(db_path=db_path)
            
            # Test data
            workflow_id = "test_workflow"
            step_id = "test_step"
            substep_id = "test_substep"
            input_data = {"input": "test"}
            output_data = {"output": "result"}
            prompt = "Test prompt"
            retrieval_context = "Test context"
            latency = 1.5
            input_tokens = 10
            output_tokens = 20
            success_status = True
            quality_score = 0.9
            evaluation_explanation = "Test evaluation"
            
            # Log step
            backend.log_step(
                workflow_id, step_id, substep_id, input_data, output_data,
                prompt, retrieval_context, latency, input_tokens, output_tokens,
                success_status, quality_score, evaluation_explanation
            )
            
            # Get logs
            logs = backend.get_logs(workflow_id)
            assert len(logs) == 1
            
            log = logs[0]
            assert log["workflow_id"] == workflow_id
            assert log["step_id"] == step_id
            assert log["substep_id"] == substep_id
            assert json.loads(log["input_data"]) == input_data
            assert json.loads(log["output_data"]) == output_data
            assert log["prompt"] == prompt
            assert log["retrieval_context"] == retrieval_context
            assert log["latency"] == latency
            assert log["input_tokens"] == input_tokens
            assert log["output_tokens"] == output_tokens
            assert log["success_status"] == success_status
            assert log["quality_score"] == quality_score
            assert log["evaluation_explanation"] == evaluation_explanation
            
        finally:
            os.unlink(db_path)


class TestJSONStorageBackend:
    """Test JSON storage backend."""
    
    def test_init_and_file_creation(self):
        """Test file initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = os.path.join(tmpdir, "state.json")
            log_file = os.path.join(tmpdir, "logs.json")
            
            backend = JSONStorageBackend(state_file=state_file, log_file=log_file)
            
            assert os.path.exists(state_file)
            assert os.path.exists(log_file)
            
            # Check initial content
            with open(state_file, 'r') as f:
                assert json.load(f) == {}
            
            with open(log_file, 'r') as f:
                assert json.load(f) == []
    
    def test_save_and_load_state(self):
        """Test saving and loading workflow state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = os.path.join(tmpdir, "state.json")
            log_file = os.path.join(tmpdir, "logs.json")
            
            backend = JSONStorageBackend(state_file=state_file, log_file=log_file)
            
            # Test data
            workflow_id = "test_workflow"
            state_data = {"key": "value", "step1": {"result": "test"}}
            version = 1
            
            # Save state
            backend.save_state(workflow_id, state_data, version)
            
            # Load state
            loaded_state = backend.load_state(workflow_id)
            assert loaded_state == state_data
            
            # Test non-existent workflow
            empty_state = backend.load_state("non_existent")
            assert empty_state == {}
    
    def test_log_step_and_get_logs(self):
        """Test logging steps and retrieving logs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = os.path.join(tmpdir, "state.json")
            log_file = os.path.join(tmpdir, "logs.json")
            
            backend = JSONStorageBackend(state_file=state_file, log_file=log_file)
            
            # Test data
            workflow_id = "test_workflow"
            step_id = "test_step"
            substep_id = "test_substep"
            input_data = {"input": "test"}
            output_data = {"output": "result"}
            prompt = "Test prompt"
            retrieval_context = "Test context"
            latency = 1.5
            input_tokens = 10
            output_tokens = 20
            success_status = True
            quality_score = 0.9
            evaluation_explanation = "Test evaluation"
            
            # Log step
            backend.log_step(
                workflow_id, step_id, substep_id, input_data, output_data,
                prompt, retrieval_context, latency, input_tokens, output_tokens,
                success_status, quality_score, evaluation_explanation
            )
            
            # Get logs
            logs = backend.get_logs(workflow_id)
            assert len(logs) == 1
            
            log = logs[0]
            assert log["workflow_id"] == workflow_id
            assert log["step_id"] == step_id
            assert log["substep_id"] == substep_id
            assert log["input_data"] == input_data
            assert log["output_data"] == output_data
            assert log["prompt"] == prompt
            assert log["retrieval_context"] == retrieval_context
            assert log["latency"] == latency
            assert log["input_tokens"] == input_tokens
            assert log["output_tokens"] == output_tokens
            assert log["success_status"] == success_status
            assert log["quality_score"] == quality_score
            assert log["evaluation_explanation"] == evaluation_explanation
