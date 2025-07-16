"""
Configuration management for SmartFlow.

This module handles configuration for different LLM providers and embedding models.
"""

import os
from typing import Any

import boto3
from langchain_community.chat_models import BedrockChat
from langchain_community.embeddings import BedrockEmbeddings, HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain_openai import ChatOpenAI


class ModelConfig:
    """Configuration class for LLM and embedding models."""
    
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "bedrock")
        self.embedding_provider = os.getenv("EMBEDDING_PROVIDER", "bedrock")
        self.bedrock_region = os.getenv("AWS_REGION", "us-east-1")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    def get_llm(self) -> Any:
        """Get the configured LLM instance."""
        if self.provider == "bedrock":
            bedrock = boto3.client(
                service_name='bedrock-runtime',
                region_name=self.bedrock_region,
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
            return BedrockChat(
                client=bedrock,
                model_id="anthropic.claude-3-7-sonnet-20241022-v1:0",
                model_kwargs={"temperature": 0.7}
            )
        elif self.provider == "openai":
            return ChatOpenAI(
                openai_api_key=self.openai_api_key,
                openai_api_base=self.openai_base_url,
                model_name="gpt-4o",
                temperature=0.7
            )
        elif self.provider == "ollama":
            return Ollama(
                model="llama3",
                base_url=self.ollama_base_url,
                temperature=0.7
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def get_embeddings(self) -> Any:
        """Get the configured embedding model instance."""
        if self.embedding_provider == "bedrock":
            bedrock = boto3.client(
                service_name='bedrock-runtime',
                region_name=self.bedrock_region,
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
            return BedrockEmbeddings(
                client=bedrock,
                model_id="amazon.titan-embed-text-v1"
            )
        elif self.embedding_provider == "huggingface":
            return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        else:
            raise ValueError(f"Unsupported embedding provider: {self.embedding_provider}")


def setup_logging() -> None:
    """Set up logging configuration."""
    import logging
    
    logging.basicConfig(
        filename='smartflow.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def load_environment() -> None:
    """Load environment variables from .env file."""
    from dotenv import load_dotenv
    load_dotenv()
