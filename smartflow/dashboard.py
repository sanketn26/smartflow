"""
Dashboard implementation for SmartFlow.

This module provides a Streamlit-based dashboard for observability and monitoring.
"""

import streamlit as st

from .storage import StorageBackend


def show_dashboard(workflow_id: str, storage_backend: StorageBackend) -> None:
    """Display the SmartFlow dashboard."""
    st.title("SmartFlow Dashboard")
    
    # Get logs for the workflow
    logs = storage_backend.get_logs(workflow_id)

    if logs:
        st.subheader("Execution Flow")
        
        # Display each log entry
        for log in logs:
            success = "✅" if log["success_status"] else "❌"
            
            # Display basic info
            st.write(
                f"Step: {log['step_id'] or 'N/A'}, "
                f"Substep: {log['substep_id'] or 'N/A'}, "
                f"Time: {log['timestamp']}, "
                f"Latency: {log['latency']:.2f}s, "
                f"Input Tokens: {log['input_tokens']}, "
                f"Output Tokens: {log['output_tokens']}, "
                f"Success: {success}"
            )
            
            # Display detailed log data
            st.json({
                "input": log["input_data"],
                "output": log["output_data"],
                "quality_score": log["quality_score"],
                "evaluation_explanation": log["evaluation_explanation"],
                "prompt": log["prompt"],
                "retrieval_context": log["retrieval_context"]
            })
            
            st.divider()
    else:
        st.write("No logs available for this workflow.")


def show_workflow_metrics(workflow_id: str, storage_backend: StorageBackend) -> None:
    """Display workflow metrics and analytics."""
    st.title("Workflow Metrics")
    
    logs = storage_backend.get_logs(workflow_id)
    
    if not logs:
        st.write("No metrics available.")
        return
    
    # Calculate metrics
    total_steps = len(logs)
    successful_steps = sum(1 for log in logs if log["success_status"])
    success_rate = (successful_steps / total_steps) * 100 if total_steps > 0 else 0
    
    avg_latency = sum(log["latency"] for log in logs) / total_steps if total_steps > 0 else 0
    total_input_tokens = sum(log["input_tokens"] for log in logs)
    total_output_tokens = sum(log["output_tokens"] for log in logs)
    avg_quality_score = sum(log["quality_score"] for log in logs) / total_steps if total_steps > 0 else 0
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Steps", total_steps)
        st.metric("Success Rate", f"{success_rate:.1f}%")
    
    with col2:
        st.metric("Avg Latency", f"{avg_latency:.2f}s")
        st.metric("Avg Quality Score", f"{avg_quality_score:.2f}")
    
    with col3:
        st.metric("Total Input Tokens", total_input_tokens)
        st.metric("Total Output Tokens", total_output_tokens)
    
    with col4:
        st.metric("Token Efficiency", f"{total_output_tokens / max(total_input_tokens, 1):.2f}")


def show_step_details(workflow_id: str, storage_backend: StorageBackend) -> None:
    """Display detailed step information."""
    st.title("Step Details")
    
    logs = storage_backend.get_logs(workflow_id)
    
    if not logs:
        st.write("No step details available.")
        return
    
    # Group logs by step
    step_logs = {}
    for log in logs:
        step_id = log["step_id"] or "Unknown"
        if step_id not in step_logs:
            step_logs[step_id] = []
        step_logs[step_id].append(log)
    
    # Display step details
    for step_id, step_log_list in step_logs.items():
        st.subheader(f"Step: {step_id}")
        
        for log in step_log_list:
            with st.expander(f"Substep: {log['substep_id'] or 'N/A'} - {log['timestamp']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Input Data:**")
                    st.json(log["input_data"])
                    
                    st.write("**Prompt:**")
                    st.text(log["prompt"])
                
                with col2:
                    st.write("**Output Data:**")
                    st.json(log["output_data"])
                    
                    st.write("**Evaluation:**")
                    st.write(f"Quality Score: {log['quality_score']:.2f}")
                    st.write(f"Success: {'✅' if log['success_status'] else '❌'}")
                    st.write(f"Explanation: {log['evaluation_explanation']}")
                
                if log["retrieval_context"]:
                    st.write("**Retrieval Context:**")
                    st.text(log["retrieval_context"])


def run_dashboard_app(workflow_id: str, storage_backend: StorageBackend) -> None:
    """Run the complete dashboard application."""
    st.set_page_config(page_title="SmartFlow Dashboard", layout="wide")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Execution Flow", "Metrics", "Step Details"]
    )
    
    # Display selected page
    if page == "Execution Flow":
        show_dashboard(workflow_id, storage_backend)
    elif page == "Metrics":
        show_workflow_metrics(workflow_id, storage_backend)
    elif page == "Step Details":
        show_step_details(workflow_id, storage_backend)
