"""Pytest configuration for LangGraph Playground."""

import os
import sys
import pytest
import asyncio
from pathlib import Path
from typing import AsyncGenerator, Generator
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient
from dotenv import load_dotenv

# Load environment variables for tests before importing app
test_env_path = Path(__file__).parent.parent / ".env.test"
if test_env_path.exists():
    load_dotenv(test_env_path)
else:
    # Fallback to main .env if test specific one doesn't exist
    load_dotenv(Path(__file__).parent.parent / ".env")

# Import app after loading environment variables
from app.main import app as fastapi_app


@pytest.fixture(scope="session")
def app() -> FastAPI:
    """Get FastAPI app for testing."""
    return fastapi_app


@pytest.fixture(scope="function")
def client(app: FastAPI) -> Generator:
    """Get test client for FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
async def async_client(app: FastAPI) -> AsyncGenerator:
    """Get async test client for FastAPI app."""
    from fastapi.testclient import TestClient

    # Use TestClient to get a working test client
    test_client = TestClient(app)
    base_url = str(test_client.base_url)
    # Create async client
    async with AsyncClient(base_url=base_url) as client:
        yield client


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for testing async code."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# Mock fixtures for testing
@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return {
        "id": "mock-response-id",
        "object": "chat.completion",
        "created": 1700000000,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "This is a mock response from OpenAI.",
                },
                "finish_reason": "stop",
            }
        ],
    }


@pytest.fixture
def mock_graph_run():
    """Mock LangGraph run result."""
    return {
        "result": "Mock graph result",
        "steps": [
            {"node": "step1", "output": "step1 output"},
            {"node": "step2", "output": "step2 output"},
        ],
    }
