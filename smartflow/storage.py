"""
Storage backend implementations for SmartFlow.

This module provides various storage backends for persisting workflow state and logs.
"""

import json
import os
import sqlite3
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List


class StorageBackend(ABC):
    """Abstract base class for storage backends."""
    
    @abstractmethod
    def save_state(self, workflow_id: str, state_data: Dict, version: int) -> None:
        """Save workflow state."""
        pass

    @abstractmethod
    def load_state(self, workflow_id: str) -> Dict:
        """Load workflow state."""
        pass

    @abstractmethod
    def log_step(
        self,
        workflow_id: str,
        step_id: str,
        substep_id: str,
        input_data: Dict,
        output_data: Dict,
        prompt: str,
        retrieval_context: str,
        latency: float,
        input_tokens: int,
        output_tokens: int,
        success_status: bool,
        quality_score: float,
        evaluation_explanation: str,
    ) -> None:
        """Log a step execution."""
        pass

    @abstractmethod
    def get_logs(self, workflow_id: str) -> List:
        """Get all logs for a workflow."""
        pass


class SQLiteStorageBackend(StorageBackend):
    """SQLite-based storage backend."""
    
    def __init__(self, db_path: str = "smartflow_state.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self) -> None:
        """Initialize the database tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS workflow_state (
                    workflow_id TEXT PRIMARY KEY,
                    state_data TEXT,
                    version INTEGER,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS step_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow_id TEXT,
                    step_id TEXT,
                    substep_id TEXT,
                    input_data TEXT,
                    output_data TEXT,
                    prompt TEXT,
                    retrieval_context TEXT,
                    timestamp TIMESTAMP,
                    latency REAL,
                    input_tokens INTEGER,
                    output_tokens INTEGER,
                    success_status BOOLEAN,
                    quality_score REAL,
                    evaluation_explanation TEXT
                )
            ''')
            conn.commit()

    def save_state(self, workflow_id: str, state_data: Dict, version: int) -> None:
        """Save workflow state to SQLite."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO workflow_state
                (workflow_id, state_data, version, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                workflow_id,
                json.dumps(state_data),
                version,
                datetime.now(),
                datetime.now()
            ))
            conn.commit()

    def load_state(self, workflow_id: str) -> Dict:
        """Load workflow state from SQLite."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT state_data FROM workflow_state WHERE workflow_id = ?', (workflow_id,))
            result = cursor.fetchone()
            return json.loads(result[0]) if result else {}

    def log_step(
        self,
        workflow_id: str,
        step_id: str,
        substep_id: str,
        input_data: Dict,
        output_data: Dict,
        prompt: str,
        retrieval_context: str,
        latency: float,
        input_tokens: int,
        output_tokens: int,
        success_status: bool,
        quality_score: float,
        evaluation_explanation: str,
    ) -> None:
        """Log a step execution to SQLite."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO step_logs
                (workflow_id, step_id, substep_id, input_data, output_data, prompt, retrieval_context, timestamp,
                 latency, input_tokens, output_tokens, success_status, quality_score, evaluation_explanation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                workflow_id,
                step_id,
                substep_id,
                json.dumps(input_data),
                json.dumps(output_data),
                prompt,
                retrieval_context,
                datetime.now(),
                latency,
                input_tokens,
                output_tokens,
                success_status,
                quality_score,
                evaluation_explanation
            ))
            conn.commit()

    def get_logs(self, workflow_id: str) -> List:
        """Get all logs for a workflow from SQLite."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM step_logs WHERE workflow_id = ?', (workflow_id,))
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]


class JSONStorageBackend(StorageBackend):
    """JSON file-based storage backend."""
    
    def __init__(self, state_file: str = "smartflow_state.json", log_file: str = "smartflow_logs.json"):
        self.state_file = state_file
        self.log_file = log_file
        self.init_files()

    def init_files(self) -> None:
        """Initialize JSON files if they don't exist."""
        if not os.path.exists(self.state_file):
            with open(self.state_file, 'w') as f:
                json.dump({}, f)
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                json.dump([], f)

    def save_state(self, workflow_id: str, state_data: Dict, version: int) -> None:
        """Save workflow state to JSON file."""
        with open(self.state_file, 'r+') as f:
            states = json.load(f)
            states[workflow_id] = {
                "state_data": state_data,
                "version": version,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            f.seek(0)
            f.truncate()
            json.dump(states, f, indent=2)

    def load_state(self, workflow_id: str) -> Dict:
        """Load workflow state from JSON file."""
        with open(self.state_file, 'r') as f:
            states = json.load(f)
            return states.get(workflow_id, {}).get("state_data", {})

    def log_step(
        self,
        workflow_id: str,
        step_id: str,
        substep_id: str,
        input_data: Dict,
        output_data: Dict,
        prompt: str,
        retrieval_context: str,
        latency: float,
        input_tokens: int,
        output_tokens: int,
        success_status: bool,
        quality_score: float,
        evaluation_explanation: str,
    ) -> None:
        """Log a step execution to JSON file."""
        with open(self.log_file, 'r+') as f:
            logs = json.load(f)
            logs.append({
                "workflow_id": workflow_id,
                "step_id": step_id,
                "substep_id": substep_id,
                "input_data": input_data,
                "output_data": output_data,
                "prompt": prompt,
                "retrieval_context": retrieval_context,
                "timestamp": datetime.now().isoformat(),
                "latency": latency,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "success_status": success_status,
                "quality_score": quality_score,
                "evaluation_explanation": evaluation_explanation
            })
            f.seek(0)
            f.truncate()
            json.dump(logs, f, indent=2)

    def get_logs(self, workflow_id: str) -> List:
        """Get all logs for a workflow from JSON file."""
        with open(self.log_file, 'r') as f:
            logs = json.load(f)
            return [log for log in logs if log["workflow_id"] == workflow_id]
