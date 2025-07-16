"""
Example workflow implementation using SmartFlow.

This example demonstrates how to create a sentiment analysis workflow
with multiple substeps including LLM and non-LLM tasks.
"""

import asyncio
import json
import os
import uuid

from smartflow import (
    Workflow, Step, Substep, ModelConfig,
    SQLiteStorageBackend, JSONStorageBackend
)
from smartflow.utils import (
    sample_python_function, 
    create_mock_documents,
    sample_data_processor
)


def create_sentiment_analysis_workflow():
    """Create a sentiment analysis workflow."""
    # Initialize configuration
    config = ModelConfig()
    llm = config.get_llm()
    embeddings = config.get_embeddings()
    
    # Choose storage backend
    storage_type = os.getenv("STORAGE_TYPE", "sqlite")
    if storage_type == "sqlite":
        storage_backend = SQLiteStorageBackend(db_path="example_workflow.db")
    else:
        storage_backend = JSONStorageBackend(
            state_file="example_state.json",
            log_file="example_logs.json"
        )
    
    # Create substeps
    # Substep 1: Sentiment Analysis with LLM
    sentiment_substep = Substep(
        id="sentiment_analysis",
        prompt_template="""
        Analyze the sentiment of the following text and provide a JSON response:
        
        Text: {input_data}
        
        Please return a JSON object with the following structure:
        {{
            "sentiment": "positive/negative/neutral",
            "confidence": 0.0-1.0,
            "reasoning": "explanation of the sentiment classification"
        }}
        """,
        llm=llm,
        embeddings=embeddings,
        success_criteria={
            "output_format": "json",
            "keywords": ["sentiment", "confidence", "reasoning"],
            "eval_prompt": """
            Evaluate if the output accurately identifies the sentiment of '{input_data}'.
            Output: {output}
            Return a score (0-1) and explanation.
            """,
            "goal": "Identify sentiment with confidence score and reasoning"
        },
        use_rag=True,
        use_past_outputs=True,
        relevance_threshold=0.7
    )
    
    # Initialize RAG with mock documents
    mock_documents = create_mock_documents()
    sentiment_substep.initialize_rag(mock_documents)
    
    # Substep 2: Text Processing with Python Function
    processing_substep = Substep(
        id="text_processing",
        non_llm_function=sample_data_processor,
        non_llm_type="python",
        success_criteria={
            "keywords": ["processed_text", "word_count"],
            "eval_prompt": """
            Evaluate if the output correctly processes the input text.
            Output: {output}
            Return a score (0-1) and explanation.
            """,
            "goal": "Process input text and extract statistics"
        }
    )
    
    # Substep 3: Summary Generation
    summary_substep = Substep(
        id="summary_generation",
        prompt_template="""
        Based on the sentiment analysis and text processing results, create a comprehensive summary:
        
        Original Text: {input_data}
        Sentiment Analysis: {sentiment_analysis}
        Text Processing: {text_processing}
        
        Please provide a summary that combines these insights.
        """,
        llm=llm,
        success_criteria={
            "min_length": 50,
            "keywords": ["summary", "analysis", "insights"],
            "eval_prompt": """
            Evaluate if the summary effectively combines sentiment analysis and text processing results.
            Summary: {output}
            Return a score (0-1) and explanation.
            """,
            "goal": "Create a comprehensive summary combining all analysis results"
        }
    )
    
    # Create step
    analysis_step = Step(
        id="comprehensive_analysis",
        substeps=[sentiment_substep, processing_substep, summary_substep],
        success_criteria={
            "min_quality_score": 0.8,
            "all_substeps_must_succeed": True,
            "eval_prompt": """
            Evaluate if the overall analysis provides comprehensive insights.
            Results: {output}
            Return a score (0-1) and explanation.
            """,
            "goal": "Produce comprehensive text analysis with sentiment, statistics, and summary"
        }
    )
    
    # Create workflow
    workflow = Workflow(
        id=str(uuid.uuid4()),
        steps=[analysis_step],
        storage_backend=storage_backend
    )
    
    return workflow


async def main():
    """Run the example workflow."""
    # Create the workflow
    workflow = create_sentiment_analysis_workflow()
    
    # Sample inputs
    test_inputs = [
        {"input_data": "I absolutely love this product! It works perfectly and exceeded my expectations."},
        {"input_data": "This is terrible. The product broke after just one day of use."},
        {"input_data": "The product is okay. Nothing special but it does what it's supposed to do."},
        {"input_data": "Amazing customer service! They resolved my issue quickly and professionally."}
    ]
    
    # Run the workflow for each test input
    for i, input_data in enumerate(test_inputs, 1):
        print(f"\n{'='*50}")
        print(f"Running Test {i}")
        print(f"{'='*50}")
        print(f"Input: {input_data['input_data']}")
        
        try:
            result = await workflow.execute(input_data, max_retries=2)
            
            print(f"\nResult:")
            print(json.dumps(result, indent=2))
            
            # Check for errors
            if "error" in result:
                print(f"❌ Workflow failed: {result['error']}")
            else:
                print("✅ Workflow completed successfully!")
                
        except Exception as e:
            print(f"❌ Error running workflow: {str(e)}")
    
    print(f"\n{'='*50}")
    print("Example workflow execution completed!")
    print(f"Workflow ID: {workflow.id}")
    print(f"{'='*50}")


if __name__ == "__main__":
    # Load environment variables
    from smartflow.config import load_environment, setup_logging
    
    load_environment()
    setup_logging()
    
    # Run the example
    asyncio.run(main())
