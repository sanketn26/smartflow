"""
Workflow state management for SmartFlow.

This module handles the persistence and management of workflow state.
"""

from typing import Any, Dict

from .storage import StorageBackend


class WorkflowState:
    """Manages the state of a workflow execution."""
    
    def __init__(self, workflow_id: str, storage_backend: StorageBackend):
        self.workflow_id = workflow_id
        self.storage_backend = storage_backend
        self.memory_buffer: Dict[str, Any] = self.load_state()
        self.version = 1

    def save_state(self) -> None:
        """Save the current state to storage."""
        self.storage_backend.save_state(self.workflow_id, self.memory_buffer, self.version)

    def load_state(self) -> Dict:
        """Load state from storage."""
        return self.storage_backend.load_state(self.workflow_id)

    def update_memory(self, key: str, value: Any) -> None:
        """Update a value in the memory buffer."""
        self.memory_buffer[key] = value

    def get_memory(self, key: str, default: Any = None) -> Any:
        """Get a value from the memory buffer."""
        return self.memory_buffer.get(key, default)

    def clear_memory(self) -> None:
        """Clear the memory buffer."""
        self.memory_buffer.clear()

    def get_all_memory(self) -> Dict[str, Any]:
        """Get all memory buffer contents."""
        return self.memory_buffer.copy()
