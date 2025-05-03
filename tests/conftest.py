"""Test configuration for the SmartSource RAG Agent."""

import os
import pytest
from typing import Dict, Any
from unittest.mock import MagicMock, patch, AsyncMock

from langchain_core.messages import AIMessage
from langchain_core.tools import tool


@pytest.fixture
def mock_env_vars():
    """Fixture to mock environment variables for testing."""
    env_vars = {
        "AZURE_OPENAI_API_KEY": "test-api-key",
        "AZURE_OPENAI_ENDPOINT": "https://test-endpoint.openai.azure.com",
        "AZURE_OPENAI_API_VERSION": "2024-02-15-preview",
        "GPT4O_DEPLOYMENT_NAME": "gpt-4o-test",
        "GPT4O_MINI_DEPLOYMENT_NAME": "gpt-4o-mini-test",
        "EMBEDDING_DEPLOYMENT_NAME": "embedding-test",
        "LANGSMITH_API_KEY": "test-langsmith-key",
        "LANGSMITH_PROJECT": "test-project",
        "LANGSMITH_TRACING": "true",
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


# Test tool for agent fixtures
@tool
def test_echo(text: str) -> str:
    """A simple tool that echoes the input."""
    return f"Echo: {text}"


@pytest.fixture
def mock_openai_agent_components():
    """Fixture to mock OpenAI agent components for testing."""
    with (
        patch("app.agents.openai_agent.get_azure_openai_client") as mock_get_client,
        patch("app.agents.openai_agent.ChatOpenAI") as mock_chat_openai,
        patch("app.agents.openai_agent.create_react_agent") as mock_create_agent,
        patch("app.agents.openai_agent.StateGraph") as mock_state_graph,
    ):

        # Mock the Azure OpenAI client
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Mock ChatOpenAI
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm

        # Mock the agent runnable
        mock_agent_runnable = MagicMock()
        mock_create_agent.return_value = mock_agent_runnable

        # Mock the state graph
        mock_builder = MagicMock()
        mock_state_graph.return_value = mock_builder
        mock_graph = MagicMock()
        mock_builder.compile.return_value = mock_graph

        # Set up mock responses for invoke methods
        mock_config_graph = MagicMock()
        mock_graph.with_config.return_value = mock_config_graph

        mock_config_graph.invoke.return_value = {
            "messages": [
                AIMessage(content="This is a test response from the mocked agent."),
            ]
        }

        # Set up mock async responses
        mock_config_graph.ainvoke = AsyncMock()
        mock_config_graph.ainvoke.return_value = {
            "messages": [
                AIMessage(
                    content="This is an async test response from the mocked agent."
                ),
            ]
        }

        yield {
            "azure_client": mock_client,
            "llm": mock_llm,
            "create_agent": mock_create_agent,
            "state_graph": mock_state_graph,
            "builder": mock_builder,
            "graph": mock_graph,
            "config_graph": mock_config_graph,
        }


@pytest.fixture
def mock_streaming_responses():
    """Fixture to mock streaming responses for agent tests."""

    class MockStreamResponse:
        def __init__(self, content: str = "This is a streaming test response."):
            self.chunks = [content[i : i + 3] for i in range(0, len(content), 3)]
            self.index = 0

        def __iter__(self):
            return self

        def __next__(self):
            if self.index < len(self.chunks):
                chunk = {"messages": [AIMessage(content=self.chunks[self.index])]}
                self.index += 1
                return chunk
            raise StopIteration

    class MockAsyncStreamResponse:
        def __init__(self, content: str = "This is an async streaming test response."):
            self.chunks = [content[i : i + 3] for i in range(0, len(content), 3)]
            self.index = 0

        def __aiter__(self):
            return self

        async def __anext__(self):
            if self.index < len(self.chunks):
                chunk = {"messages": [AIMessage(content=self.chunks[self.index])]}
                self.index += 1
                return chunk
            raise StopAsyncIteration

    return {
        "stream": MockStreamResponse,
        "astream": MockAsyncStreamResponse,
    }


@pytest.fixture
def mock_tool_call_responses():
    """Fixture to mock tool call responses for agent tests."""

    def create_tool_call_response(tool_name: str, tool_input: Dict[str, Any]):
        return {
            "messages": [
                AIMessage(
                    content=None,
                    tool_calls=[
                        {
                            "id": "call_123",
                            "type": "function",
                            "function": {
                                "name": tool_name,
                                "arguments": tool_input,
                            },
                        }
                    ],
                )
            ],
            "tool_calls": [
                {
                    "id": "call_123",
                    "type": "function",
                    "function": {
                        "name": tool_name,
                        "arguments": tool_input,
                    },
                }
            ],
        }

    def create_tool_result_response(result: str):
        return {
            "messages": [
                AIMessage(content=result),
            ]
        }

    return {
        "create_tool_call": create_tool_call_response,
        "create_tool_result": create_tool_result_response,
    }
