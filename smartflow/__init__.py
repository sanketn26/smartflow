"""
SmartFlow: A modular AI workflow engine with prompt feedback loops, LLM/non-LLM tasks, and token tracking.

This package provides a comprehensive framework for building and orchestrating AI workflows
with support for various LLM providers, RAG capabilities, and extensive observability.
"""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("smartflow")
except PackageNotFoundError:
    __version__ = "unknown"

from .workflow import Workflow
from .step import Step
from .substep import Substep
from .config import ModelConfig
from .storage import StorageBackend, SQLiteStorageBackend, JSONStorageBackend
from .state import WorkflowState
from .callbacks import SmartFlowCallbackHandler
from .dashboard import show_dashboard

__all__ = [
    "Workflow",
    "Step", 
    "Substep",
    "ModelConfig",
    "StorageBackend",
    "SQLiteStorageBackend",
    "JSONStorageBackend",
    "WorkflowState",
    "SmartFlowCallbackHandler",
    "show_dashboard",
    "__version__",
]
