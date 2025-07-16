#!/usr/bin/env python3
"""
Script to set up development environment for SmartFlow.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd: str, description: str):
    """Run a command and handle errors."""
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error: {description} failed")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        return False
    
    print(f"Success: {description}")
    print(f"Output: {result.stdout}")
    return True


def main():
    """Main setup function."""
    print("Setting up SmartFlow development environment...")
    
    # Check if Poetry is installed
    if not run_command("poetry --version", "Check Poetry installation"):
        print("Please install Poetry first: https://python-poetry.org/docs/#installation")
        sys.exit(1)
    
    # Install dependencies
    if not run_command("poetry install", "Install dependencies"):
        sys.exit(1)
    
    # Set up pre-commit hooks if available
    if run_command("poetry run pre-commit --version", "Check pre-commit availability"):
        run_command("poetry run pre-commit install", "Install pre-commit hooks")
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("Creating .env file from .env.example...")
        env_file.write_text(env_example.read_text())
        print("Please edit .env with your configuration")
    
    # Run tests to verify setup
    print("\nRunning tests to verify setup...")
    if run_command("poetry run pytest tests/ -v", "Run test suite"):
        print("\n✅ Development environment setup complete!")
        print("\nNext steps:")
        print("1. Edit .env with your LLM provider configuration")
        print("2. Run 'poetry run python examples/sentiment_analysis.py' to test")
        print("3. Run 'poetry run smartflow --help' to see CLI options")
    else:
        print("\n❌ Some tests failed. Please check the output above.")


if __name__ == "__main__":
    main()
