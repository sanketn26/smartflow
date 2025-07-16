"""
Callback handlers for SmartFlow.

This module provides callback handlers for tracking workflow execution.
"""

import logging
from typing import Any, Dict

from langchain_core.callbacks import BaseCallbackHandler

from .storage import StorageBackend

logger = logging.getLogger(__name__)


class SmartFlowCallbackHandler(BaseCallbackHandler):
    """Callback handler for SmartFlow workflows."""
    
    def __init__(self, workflow_id: str, storage_backend: StorageBackend):
        self.workflow_id = workflow_id
        self.storage_backend = storage_backend

    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs) -> None:
        """Called when a chain starts execution."""
        logger.info(f"Chain started: {serialized.get('id', 'unknown')} with inputs: {inputs}")

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs) -> None:
        """Called when a chain ends execution."""
        metadata = kwargs.get("metadata", {})
        step_id = metadata.get("step_id", "")
        substep_id = metadata.get("substep_id", "")
        prompt = metadata.get("prompt", "")
        retrieval_context = metadata.get("retrieval_context", "")
        latency = metadata.get("latency", 0)
        input_tokens = metadata.get("input_tokens", 0)
        output_tokens = metadata.get("output_tokens", 0)
        success_status = metadata.get("success_status", False)
        quality_score = metadata.get("quality_score", 0.0)
        evaluation_explanation = metadata.get("evaluation_explanation", "")

        self.storage_backend.log_step(
            workflow_id=self.workflow_id,
            step_id=step_id,
            substep_id=substep_id,
            input_data=kwargs.get("inputs", {}),
            output_data=outputs,
            prompt=prompt,
            retrieval_context=retrieval_context,
            latency=latency,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            success_status=success_status,
            quality_score=quality_score,
            evaluation_explanation=evaluation_explanation
        )
