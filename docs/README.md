# SmartFlow Documentation

## Overview

SmartFlow is a modular AI workflow engine that provides a comprehensive framework for building and orchestrating AI workflows with support for various LLM providers, RAG capabilities, and extensive observability.

## Key Features

- **Multi-LLM Support**: Works with AWS Bedrock, OpenAI, and Ollama
- **RAG Integration**: Built-in support for Retrieval-Augmented Generation
- **Modular Architecture**: Workflows composed of steps and substeps
- **Quality Evaluation**: Automatic quality scoring and custom evaluation
- **State Management**: Persistent workflow state with resume capabilities
- **Observability**: Comprehensive logging and dashboard
- **Non-LLM Tasks**: Support for custom Python functions and API calls

## Architecture

### Core Components

1. **Workflow**: The main orchestrator that manages step execution
2. **Step**: A collection of substeps that execute together
3. **Substep**: Individual execution units (LLM or non-LLM tasks)
4. **Storage Backend**: Persistent storage for state and logs
5. **Model Config**: Configuration for LLM and embedding providers

### Flow Diagram

```
Workflow
├── Step 1
│   ├── Substep 1 (LLM Task)
│   ├── Substep 2 (Python Function)
│   └── Substep 3 (LLM Task)
├── Step 2
│   └── Substep 4 (API Call)
└── Step 3
    └── Substep 5 (LLM Task)
```

## Quick Start

### Installation

```bash
pip install smartflow
```

### Basic Usage

```python
import asyncio
from smartflow import Workflow, Step, Substep, ModelConfig, SQLiteStorageBackend

# Configure models
config = ModelConfig()
llm = config.get_llm()
embeddings = config.get_embeddings()

# Create storage backend
storage = SQLiteStorageBackend()

# Create substep
substep = Substep(
    id="sentiment_analysis",
    prompt_template="Analyze sentiment: {input_data}",
    llm=llm,
    success_criteria={"keywords": ["sentiment"]}
)

# Create step
step = Step(
    id="analysis_step",
    substeps=[substep],
    success_criteria={"min_quality_score": 0.8}
)

# Create workflow
workflow = Workflow(
    id="sentiment_workflow",
    steps=[step],
    storage_backend=storage
)

# Execute workflow
async def main():
    result = await workflow.execute({"input_data": "I love this product!"})
    print(result)

asyncio.run(main())
```

## Configuration

### Environment Variables

```bash
# LLM Provider (bedrock, openai, ollama)
LLM_PROVIDER=bedrock

# Embedding Provider (bedrock, huggingface)
EMBEDDING_PROVIDER=bedrock

# AWS Configuration (for Bedrock)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# OpenAI Configuration
OPENAI_API_KEY=your_openai_key
OPENAI_BASE_URL=https://api.openai.com/v1

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434

# Storage Configuration
STORAGE_TYPE=sqlite  # or json
```

## Advanced Features

### RAG Integration

```python
substep = Substep(
    id="rag_substep",
    prompt_template="Answer based on context: {input_data}",
    llm=llm,
    embeddings=embeddings,
    use_rag=True
)

# Initialize with documents
documents = ["Document 1 content", "Document 2 content"]
substep.initialize_rag(documents)
```

### Custom Success Criteria

```python
success_criteria = {
    "output_format": "json",
    "keywords": ["required", "keywords"],
    "max_length": 1000,
    "min_quality_score": 0.8,
    "eval_prompt": "Evaluate if output meets requirements: {output}"
}
```

### Non-LLM Tasks

```python
def custom_function(inputs):
    data = inputs.get("input_data", "")
    return {"result": f"Processed: {data}"}

substep = Substep(
    id="custom_task",
    non_llm_function=custom_function,
    non_llm_type="python"
)
```

## Dashboard

Launch the dashboard to monitor workflow execution:

```bash
smartflow dashboard --db-path smartflow_state.db
```

## CLI Usage

```bash
# Run a workflow
smartflow run --input-text "Your input text here"

# Run with input file
smartflow run --input-file input.json --output-file output.json

# Launch dashboard
smartflow dashboard

# List workflows
smartflow list
```

## API Reference

See the individual module documentation for detailed API reference:

- [Workflow](api/workflow.md)
- [Step](api/step.md)
- [Substep](api/substep.md)
- [Storage](api/storage.md)
- [Config](api/config.md)
