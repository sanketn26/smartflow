# SmartFlow

A modular AI workflow engine with prompt feedback loops, LLM/non-LLM tasks, and token tracking.

## Features

- **Multi-LLM Support**: Works with AWS Bedrock, OpenAI, and Ollama
- **RAG Integration**: Built-in support for Retrieval-Augmented Generation
- **Modular Architecture**: Workflows composed of steps and substeps
- **Quality Evaluation**: Automatic quality scoring and custom evaluation prompts
- **State Management**: Persistent workflow state with resume capabilities
- **Observability**: Comprehensive logging and Streamlit dashboard
- **Non-LLM Tasks**: Support for custom Python functions and API calls

## Installation

```bash
pip install smartflow
```

## Quick Start

```python
import asyncio
from smartflow import Workflow, Step, Substep, ModelConfig, SQLiteStorageBackend

# Configure models
config = ModelConfig()
llm = config.get_llm()

# Create storage backend
storage = SQLiteStorageBackend()

# Create substep
substep = Substep(
    id="sentiment_analysis",
    prompt_template="Analyze sentiment: {input_data}",
    llm=llm,
    success_criteria={"keywords": ["sentiment"]}
)

# Create step and workflow
step = Step(id="analysis", substeps=[substep], success_criteria={})
workflow = Workflow(id="sentiment_workflow", steps=[step], storage_backend=storage)

# Execute
async def main():
    result = await workflow.execute({"input_data": "I love this product!"})
    print(result)

asyncio.run(main())
```

## CLI Usage

```bash
# Run a workflow
smartflow run --input-text "Your input text here"

# Launch dashboard
smartflow dashboard

# List workflows
smartflow list
```

## Configuration

Set environment variables for your preferred LLM provider:

```bash
# For AWS Bedrock
export LLM_PROVIDER=bedrock
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret

# For OpenAI
export LLM_PROVIDER=openai
export OPENAI_API_KEY=your_key

# For Ollama
export LLM_PROVIDER=ollama
export OLLAMA_BASE_URL=http://localhost:11434
```

## Documentation

See the [documentation](docs/README.md) for detailed usage instructions and API reference.

## Development

```bash
# Install with Poetry
poetry install

# Run tests
poetry run pytest

# Run example
poetry run python examples/sentiment_analysis.py
```

## License

MIT License - see [LICENSE](LICENSE) for details. 
