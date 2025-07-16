"""
Step implementation for SmartFlow.

This module contains the Step class which represents a collection of substeps that execute together.
"""

import json
import logging
from typing import Dict, List

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from .callbacks import SmartFlowCallbackHandler
from .state import WorkflowState
from .substep import Substep

logger = logging.getLogger(__name__)


class Step:
    """Represents a collection of substeps that execute together."""
    
    def __init__(self, id: str, substeps: List[Substep], success_criteria: Dict):
        self.id = id
        self.substeps = substeps
        self.success_criteria = success_criteria

    async def execute(
        self,
        input_data: Dict,
        workflow_state: WorkflowState,
        callback_handler: SmartFlowCallbackHandler
    ) -> Dict:
        """Execute all substeps in this step."""
        output = {}
        substep_results = []
        
        for substep in self.substeps:
            input_data["step_id"] = self.id
            result = await substep.execute(input_data, workflow_state.memory_buffer, callback_handler, self.id)
            output[substep.id] = result
            substep_results.append(result["metrics"])
            input_data = result["output"]

        # Evaluate the overall step performance
        step_evaluation = self.evaluate_step(substep_results, output)
        
        # Log the step completion
        callback_handler.on_chain_end(
            output,
            inputs=input_data,
            metadata={
                "step_id": self.id,
                "substep_id": "",
                "prompt": "",
                "retrieval_context": "",
                "success_status": step_evaluation["success_status"],
                "quality_score": step_evaluation["quality_score"],
                "evaluation_explanation": step_evaluation["evaluation_explanation"],
                "latency": sum(r["latency"] for r in substep_results),
                "input_tokens": sum(r["input_tokens"] for r in substep_results),
                "output_tokens": sum(r["output_tokens"] for r in substep_results)
            }
        )

        return {
            "output": output,
            "metrics": step_evaluation
        }

    def evaluate_step(self, substep_results: List[Dict], output: Dict) -> Dict:
        """Evaluate the overall step performance."""
        success_status = True
        quality_score = 1.0
        explanation = []

        # Calculate average quality score
        quality_scores = [r["quality_score"] for r in substep_results]
        avg_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        all_succeeded = all(r["success_status"] for r in substep_results)

        # Check minimum quality score requirement
        if "min_quality_score" in self.success_criteria:
            if avg_quality_score < self.success_criteria["min_quality_score"]:
                success_status = False
                quality_score *= avg_quality_score
                explanation.append(
                    f"Average quality score {avg_quality_score:.2f} below threshold "
                    f"{self.success_criteria['min_quality_score']}"
                )

        # Check if all substeps must succeed
        if self.success_criteria.get("all_substeps_must_succeed", False) and not all_succeeded:
            success_status = False
            quality_score *= 0.8
            explanation.append("Not all substeps succeeded.")

        # Custom step evaluation with LLM
        if "eval_prompt" in self.success_criteria and self.substeps:
            try:
                eval_prompt = ChatPromptTemplate.from_template(self.success_criteria["eval_prompt"])
                eval_chain = eval_prompt | self.substeps[0].llm | StrOutputParser()
                eval_input = {
                    "goal": self.success_criteria.get("goal", ""),
                    "output": json.dumps(output)
                }
                result = eval_chain.invoke(eval_input)
                score = float(result.split("\n")[0].strip())
                quality_score *= score
                explanation.append(result)
            except Exception as e:
                explanation.append(f"Step evaluation failed: {str(e)}")

        return {
            "success_status": success_status,
            "quality_score": max(0.0, min(1.0, quality_score)),
            "evaluation_explanation": "\n".join(explanation) if explanation else "No issues detected."
        }
