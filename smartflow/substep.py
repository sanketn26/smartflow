"""
Substep implementation for SmartFlow.

This module contains the Substep class which represents individual execution units within a workflow step.
"""

import json
import logging
import os
import re
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableSequence
from sklearn.metrics.pairwise import cosine_similarity

from .callbacks import SmartFlowCallbackHandler

logger = logging.getLogger(__name__)


class Substep:
    """Represents a single execution unit within a workflow step."""
    
    def __init__(
        self,
        id: str,
        prompt_template: Optional[str] = None,
        llm=None,
        embeddings=None,
        success_criteria: Optional[Dict] = None,
        use_rag: bool = False,
        web_search: bool = False,
        use_past_outputs: bool = False,
        relevance_threshold: float = 0.7,
        non_llm_function: Optional[Callable] = None,
        non_llm_type: Optional[str] = None,
    ):
        self.id = id
        self.prompt_template = ChatPromptTemplate.from_template(prompt_template) if prompt_template else None
        self.llm = llm
        self.embeddings = embeddings
        self.success_criteria = success_criteria or {}
        self.use_rag = use_rag
        self.web_search = web_search
        self.use_past_outputs = use_past_outputs
        self.relevance_threshold = relevance_threshold
        self.non_llm_function = non_llm_function
        self.non_llm_type = non_llm_type
        self.vector_store = None

    def initialize_rag(self, documents: List[str]) -> None:
        """Initialize RAG with provided documents."""
        if self.use_rag and self.embeddings:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = text_splitter.split_text("\n".join(documents))
            docs = [Document(page_content=chunk) for chunk in chunks]
            self.vector_store = FAISS.from_documents(docs, self.embeddings)

    def extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text for RAG enhancement."""
        words = re.findall(r'\b\w+\b', text.lower())
        return [word for word in words if len(word) > 3 and word not in {'this', 'that', 'with', 'from'}][:5]

    def enhance_prompt(self, base_prompt: str, memory_buffer: Dict, step_id: str) -> str:
        """Enhance the prompt with RAG and context."""
        if not self.use_rag or not self.vector_store or not self.llm:
            return base_prompt
        
        keywords = set()
        if "input_data" in memory_buffer:
            keywords.update(self.extract_keywords(memory_buffer["input_data"]))
        
        for substep_id, output in memory_buffer.items():
            if substep_id.startswith(step_id) and "result" in output:
                keywords.update(self.extract_keywords(output["result"]))
        
        enhanced_prompt = f"{base_prompt}\nRelevant keywords: {', '.join(keywords)}"
        
        refine_prompt = ChatPromptTemplate.from_template(
            "Refine this prompt to be clear, focused, and aligned with the goal '{goal}', "
            "incorporating the provided keywords:\nPrompt: {prompt}"
        )
        
        refine_chain = refine_prompt | self.llm | StrOutputParser()
        return refine_chain.invoke({
            "prompt": enhanced_prompt,
            "goal": self.success_criteria.get("goal", "")
        })

    def extract_token_usage(self, result: Any) -> Tuple[int, int]:
        """Extract token usage from LLM result."""
        try:
            if hasattr(result, 'usage_metadata'):
                return (
                    result.usage_metadata.get('input_tokens', 0),
                    result.usage_metadata.get('output_tokens', 0)
                )
            elif hasattr(result, 'metadata') and 'usage' in result.metadata:
                usage = result.metadata['usage']
                return usage.get('input_tokens', 0), usage.get('output_tokens', 0)
            return 0, 0
        except Exception as e:
            logger.warning(f"Failed to extract token usage: {str(e)}")
            return 0, 0

    def evaluate_output(self, inputs: Dict, output: str) -> Dict:
        """Evaluate the output quality based on success criteria."""
        success_status = True
        quality_score = 1.0
        explanation = []

        # Check output format
        if "output_format" in self.success_criteria:
            if self.success_criteria["output_format"] == "json":
                try:
                    json.loads(output)
                except json.JSONDecodeError:
                    success_status = False
                    quality_score *= 0.5
                    explanation.append("Output is not valid JSON.")

        # Check required keywords
        if "keywords" in self.success_criteria:
            missing_keywords = [
                kw for kw in self.success_criteria["keywords"]
                if kw.lower() not in output.lower()
            ]
            if missing_keywords:
                success_status = False
                quality_score *= 0.8
                explanation.append(f"Missing keywords: {', '.join(missing_keywords)}")

        # Check output length
        if "max_length" in self.success_criteria:
            if len(output) > self.success_criteria["max_length"]:
                success_status = False
                quality_score *= 0.7
                explanation.append(f"Output exceeds max length of {self.success_criteria['max_length']} characters.")

        # Custom evaluation with LLM
        if "eval_prompt" in self.success_criteria and self.llm:
            eval_prompt = ChatPromptTemplate.from_template(self.success_criteria["eval_prompt"])
            eval_chain = eval_prompt | self.llm | StrOutputParser()
            eval_input = {
                "goal": self.success_criteria.get("goal", ""),
                "output": output,
                "input_data": inputs.get("input_data", "")
            }
            
            try:
                result = eval_chain.invoke(eval_input)
                score = float(result.split("\n")[0].strip())
                quality_score *= score
                explanation.append(result)
            except Exception as e:
                explanation.append(f"Evaluation failed: {str(e)}")

        return {
            "success_status": success_status,
            "quality_score": max(0.0, min(1.0, quality_score)),
            "evaluation_explanation": "\n".join(explanation) if explanation else "No issues detected."
        }

    def get_relevant_past_outputs(self, current_input: Dict, memory_buffer: Dict) -> Dict:
        """Get relevant past outputs based on similarity."""
        if not self.use_past_outputs or not self.embeddings:
            return {}
        
        relevant_outputs = {}
        current_embedding = self.embeddings.embed_query(current_input.get("input_data", ""))
        
        for substep_id, output in memory_buffer.items():
            if substep_id != self.id and "result" in output:
                past_output_text = output["result"]
                past_embedding = self.embeddings.embed_query(past_output_text)
                
                if current_embedding and past_embedding:
                    similarity = cosine_similarity([current_embedding], [past_embedding])[0][0]
                    if similarity >= self.relevance_threshold:
                        relevant_outputs[substep_id] = past_output_text
        
        return relevant_outputs

    def get_chain(self):
        """Get the execution chain for this substep."""
        if self.non_llm_function:
            return RunnableLambda(self.non_llm_function)
        
        def retrieve_context(inputs):
            if self.use_rag and self.vector_store:
                query = inputs.get("input_data", "")
                results = self.vector_store.similarity_search(query, k=3)
                context = "\n".join([doc.page_content for doc in results])
                inputs["retrieval_context"] = context
            return inputs

        def format_output(output):
            return {"result": output}

        chain = RunnableSequence(
            RunnableLambda(retrieve_context) if self.use_rag else RunnableLambda(lambda x: x),
            self.prompt_template,
            self.llm,
            RunnableLambda(format_output)
        )
        return chain

    async def execute(
        self,
        input_data: Dict,
        memory_buffer: Dict,
        callback_handler: SmartFlowCallbackHandler,
        step_id: str
    ) -> Dict:
        """Execute the substep."""
        try:
            start_time = time.time()
            
            # Get relevant past outputs
            past_outputs = self.get_relevant_past_outputs(input_data, memory_buffer)
            prompt_input = {**input_data, **memory_buffer, **past_outputs}
            
            # Prepare prompt
            if self.prompt_template and self.llm:
                base_prompt = self.prompt_template.format(**prompt_input)
                prompt_text = self.enhance_prompt(base_prompt, memory_buffer, step_id)
            else:
                prompt_text = ""

            # Handle test mode
            if os.getenv("TEST_MODE") == "true":
                output = {"result": f"Mock response for substep {self.id}"}
                evaluation = {
                    "success_status": True,
                    "quality_score": 1.0,
                    "evaluation_explanation": "Mock evaluation successful."
                }
                latency = 0.1
                input_tokens = output_tokens = 0
            else:
                # Execute the chain
                chain = self.get_chain()
                result = await chain.ainvoke(
                    prompt_input,
                    config={
                        "callbacks": [callback_handler],
                        "metadata": {
                            "step_id": step_id,
                            "substep_id": self.id,
                            "prompt": prompt_text,
                            "retrieval_context": prompt_input.get("retrieval_context", ""),
                            "latency": 0,
                            "input_tokens": 0,
                            "output_tokens": 0
                        }
                    }
                )
                
                output = result
                input_tokens, output_tokens = self.extract_token_usage(result) if self.llm else (0, 0)
                evaluation = self.evaluate_output(prompt_input, str(output["result"]))
                latency = time.time() - start_time

                # Log the execution
                callback_handler.on_chain_end(
                    output,
                    inputs=prompt_input,
                    metadata={
                        "step_id": step_id,
                        "substep_id": self.id,
                        "prompt": prompt_text,
                        "retrieval_context": prompt_input.get("retrieval_context", ""),
                        "success_status": evaluation["success_status"],
                        "quality_score": evaluation["quality_score"],
                        "evaluation_explanation": evaluation["evaluation_explanation"],
                        "latency": latency,
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens
                    }
                )

            # Update memory buffer
            memory_buffer[self.id] = output
            
            return {
                "output": output,
                "metrics": {
                    "latency": latency,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "quality_score": evaluation["quality_score"],
                    "success_status": evaluation["success_status"],
                    "evaluation_explanation": evaluation["evaluation_explanation"]
                }
            }
            
        except Exception as e:
            logger.error(f"Error in substep {self.id}: {str(e)}")
            
            evaluation = {
                "success_status": False,
                "quality_score": 0.0,
                "evaluation_explanation": f"Execution failed: {str(e)}"
            }
            
            return {
                "output": {"error": str(e)},
                "metrics": {
                    "latency": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "quality_score": evaluation["quality_score"],
                    "success_status": evaluation["success_status"],
                    "evaluation_explanation": evaluation["evaluation_explanation"]
                }
            }
