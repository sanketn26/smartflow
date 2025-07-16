# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of SmartFlow
- Support for multiple LLM providers (AWS Bedrock, OpenAI, Ollama)
- RAG integration with FAISS vector store
- Modular workflow architecture with steps and substeps
- Quality evaluation with custom success criteria
- Persistent state management with SQLite and JSON backends
- Comprehensive logging and observability
- Streamlit dashboard for monitoring
- Command-line interface
- Support for non-LLM tasks (Python functions, API calls)
- Token usage tracking and metrics
- Workflow resume functionality
- Extensive test coverage
- Documentation and examples

### Changed
- Refactored monolithic workflow.py into modular components
- Improved error handling and logging
- Enhanced type annotations throughout codebase

### Fixed
- Import path issues in package structure
- Type annotation errors in substep initialization

## [0.1.0] - 2025-07-16

### Added
- Initial package structure with Poetry
- Core workflow engine functionality
- Basic documentation and examples
