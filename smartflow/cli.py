"""
Command-line interface for SmartFlow.

This module provides a CLI for running workflows and managing the SmartFlow system.
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import uuid
from typing import Dict, Any

from .config import ModelConfig, load_environment, setup_logging
from .storage import SQLiteStorageBackend, JSONStorageBackend
from .workflow import Workflow
from .step import Step
from .substep import Substep
from .utils import sample_python_function, create_mock_documents


def create_sample_workflow() -> Workflow:
    """Create a sample workflow for testing."""
    # Initialize configuration
    config = ModelConfig()
    llm = config.get_llm()
    embeddings = config.get_embeddings()
    
    # Choose storage backend
    storage_type = os.getenv("STORAGE_TYPE", "sqlite")
    if storage_type == "sqlite":
        storage_backend = SQLiteStorageBackend(db_path="smartflow_state.db")
    else:
        storage_backend = JSONStorageBackend(
            state_file="smartflow_state.json",
            log_file="smartflow_logs.json"
        )
    
    # Create substeps
    substep1 = Substep(
        id="sentiment_analysis",
        prompt_template="Analyze the following input for sentiment: {input_data}",
        llm=llm,
        embeddings=embeddings,
        success_criteria={
            "output_format": "json",
            "keywords": ["sentiment", "confidence"],
            "eval_prompt": "Evaluate if the output accurately identifies the sentiment of '{input_data}'.\nOutput: {output}\nReturn a score (0-1) and explanation.",
            "goal": "Identify sentiment with confidence score"
        },
        use_rag=True,
        use_past_outputs=True,
        relevance_threshold=0.7
    )
    
    # Initialize RAG for the substep
    mock_documents = create_mock_documents()
    substep1.initialize_rag(mock_documents)
    
    substep2 = Substep(
        id="text_processing",
        non_llm_function=sample_python_function,
        non_llm_type="python",
        success_criteria={
            "keywords": ["processed"],
            "eval_prompt": "Evaluate if the output correctly processes the input.\nOutput: {output}\nReturn a score (0-1) and explanation.",
            "goal": "Process input with Python function"
        }
    )
    
    # Create step
    step1 = Step(
        id="analysis_step",
        substeps=[substep1, substep2],
        success_criteria={
            "min_quality_score": 0.8,
            "all_substeps_must_succeed": True,
            "eval_prompt": "Evaluate if the output forms a coherent analysis report.\nOutput: {output}\nReturn a score (0-1) and explanation.",
            "goal": "Produce a coherent analysis report"
        }
    )
    
    # Create workflow
    workflow = Workflow(
        id=str(uuid.uuid4()),
        steps=[step1],
        storage_backend=storage_backend
    )
    
    return workflow


def run_workflow_command(args: argparse.Namespace) -> None:
    """Run a workflow with the given input."""
    try:
        # Load environment and setup logging
        load_environment()
        setup_logging()
        
        # Create sample workflow
        workflow = create_sample_workflow()
        
        # Prepare input
        if args.input_file:
            with open(args.input_file, 'r') as f:
                input_data = json.load(f)
        else:
            input_data = {"input_data": args.input_text}
        
        # Run workflow
        result = asyncio.run(workflow.execute(input_data, max_retries=args.max_retries))
        
        # Output result
        if args.output_file:
            with open(args.output_file, 'w') as f:
                json.dump(result, f, indent=2)
        else:
            print(json.dumps(result, indent=2))
            
        print(f"Workflow {workflow.id} completed successfully!")
        
    except Exception as e:
        print(f"Error running workflow: {str(e)}", file=sys.stderr)
        sys.exit(1)


def dashboard_command(args: argparse.Namespace) -> None:
    """Launch the dashboard."""
    try:
        import streamlit as st
        from .dashboard import run_dashboard_app
        from .storage import SQLiteStorageBackend
        
        storage_backend = SQLiteStorageBackend(db_path=args.db_path)
        
        # This would need to be run with streamlit run
        print("To run the dashboard, use: streamlit run -m smartflow.dashboard")
        print(f"Database path: {args.db_path}")
        
    except ImportError:
        print("Streamlit is required for the dashboard. Install it with: pip install streamlit")
        sys.exit(1)


def list_workflows_command(args: argparse.Namespace) -> None:
    """List all workflows in the storage backend."""
    try:
        if args.storage_type == "sqlite":
            storage_backend = SQLiteStorageBackend(db_path=args.db_path)
        else:
            storage_backend = JSONStorageBackend(
                state_file=args.state_file,
                log_file=args.log_file
            )
        
        # This would need to be implemented in the storage backend
        print("Workflow listing not yet implemented")
        
    except Exception as e:
        print(f"Error listing workflows: {str(e)}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="SmartFlow - A modular AI workflow engine"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Run workflow command
    run_parser = subparsers.add_parser("run", help="Run a workflow")
    run_parser.add_argument(
        "--input-text",
        type=str,
        help="Input text for the workflow"
    )
    run_parser.add_argument(
        "--input-file",
        type=str,
        help="Input JSON file for the workflow"
    )
    run_parser.add_argument(
        "--output-file",
        type=str,
        help="Output JSON file for the results"
    )
    run_parser.add_argument(
        "--max-retries",
        type=int,
        default=1,
        help="Maximum number of retries for failed steps"
    )
    
    # Dashboard command
    dashboard_parser = subparsers.add_parser("dashboard", help="Launch the dashboard")
    dashboard_parser.add_argument(
        "--db-path",
        type=str,
        default="smartflow_state.db",
        help="Path to the SQLite database"
    )
    
    # List workflows command
    list_parser = subparsers.add_parser("list", help="List all workflows")
    list_parser.add_argument(
        "--storage-type",
        type=str,
        choices=["sqlite", "json"],
        default="sqlite",
        help="Storage backend type"
    )
    list_parser.add_argument(
        "--db-path",
        type=str,
        default="smartflow_state.db",
        help="Path to the SQLite database"
    )
    list_parser.add_argument(
        "--state-file",
        type=str,
        default="smartflow_state.json",
        help="Path to the JSON state file"
    )
    list_parser.add_argument(
        "--log-file",
        type=str,
        default="smartflow_logs.json",
        help="Path to the JSON log file"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.command == "run":
        if not args.input_text and not args.input_file:
            print("Error: Either --input-text or --input-file must be provided")
            sys.exit(1)
        run_workflow_command(args)
    elif args.command == "dashboard":
        dashboard_command(args)
    elif args.command == "list":
        list_workflows_command(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
