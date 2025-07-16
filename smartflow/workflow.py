"""
Workflow implementation for SmartFlow.

This module contains the main Workflow class that orchestrates the execution of steps.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from .callbacks import SmartFlowCallbackHandler
from .state import WorkflowState
from .step import Step
from .storage import StorageBackend

logger = logging.getLogger(__name__)


class Workflow:
    """Main workflow orchestrator that manages the execution of steps."""
    
    def __init__(self, id: str, steps: List[Step], storage_backend: StorageBackend):
        self.id = id
        self.steps = steps
        self.state = WorkflowState(id, storage_backend)
        self.callback_handler = SmartFlowCallbackHandler(id, storage_backend)

    async def execute(
        self,
        initial_input: Dict,
        resume_from_step: Optional[str] = None,
        max_retries: int = 1
    ) -> Dict:
        """Execute the workflow."""
        self.state.load_state()
        
        # Determine starting step
        start_idx = 0
        if resume_from_step:
            start_idx = next(
                (i for i, step in enumerate(self.steps) if step.id == resume_from_step),
                0
            )

        output = initial_input
        
        # Execute each step
        for step in self.steps[start_idx:]:
            retries = 0
            
            while retries <= max_retries:
                try:
                    result = await step.execute(output, self.state, self.callback_handler)
                    
                    if result["metrics"]["success_status"]:
                        output = result["output"]
                        self.state.save_state()
                        break
                    else:
                        retries += 1
                        logger.warning(f"Step {step.id} failed evaluation, retry {retries}/{max_retries}")
                        
                        if retries > max_retries:
                            logger.error(f"Step {step.id} failed after {max_retries} retries")
                            output = {"error": f"Step {step.id} failed evaluation"}
                            break
                            
                except Exception as e:
                    logger.error(f"Step {step.id} failed: {str(e)}")
                    retries += 1
                    
                    if retries > max_retries:
                        logger.error(f"Step {step.id} failed after {max_retries} retries: {str(e)}")
                        output = {"error": str(e)}
                        break
            
            # Break if there's an error
            if "error" in output:
                break
        
        return output

    def version(self) -> Dict:
        """Get workflow version information."""
        return {
            "workflow_id": self.id,
            "version": 1,
            "steps": [step.id for step in self.steps],
            "timestamp": datetime.now().isoformat()
        }

    def get_step_by_id(self, step_id: str) -> Optional[Step]:
        """Get a step by its ID."""
        for step in self.steps:
            if step.id == step_id:
                return step
        return None

    def get_step_count(self) -> int:
        """Get the total number of steps in the workflow."""
        return len(self.steps)

    def get_step_ids(self) -> List[str]:
        """Get all step IDs in the workflow."""
        return [step.id for step in self.steps]
