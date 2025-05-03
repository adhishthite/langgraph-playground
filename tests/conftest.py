"""Test configuration for the SmartSource RAG Agent."""

import os
import pytest
from unittest.mock import patch


@pytest.fixture
def mock_env_vars():
    """Fixture to mock environment variables for testing."""
    env_vars = {
        "AZURE_OPENAI_API_KEY": "test-api-key",
        "AZURE_OPENAI_ENDPOINT": "https://test-endpoint.openai.azure.com",
        "AZURE_OPENAI_API_VERSION": "2024-02-15-preview",
        "LANGCHAIN_API_KEY": "test-langsmith-key",
        "LANGCHAIN_PROJECT": "test-project",
        "LANGCHAIN_TRACING_V2": "true",
        "ES_HOST": "localhost",
        "ES_PORT": "9200",
        "ES_INDEX_NAMES": "test-index-1,test-index-2",
        "LOG_LEVEL": "DEBUG",
        "DEFAULT_AGENT": "test-agent",
        "MAX_DOCUMENT_COUNT": "10",
        "RRF_K_FACTOR": "50.0",
    }
    with patch.dict(os.environ, env_vars, clear=True):
        yield env_vars
