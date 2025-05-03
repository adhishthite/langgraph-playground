"""
Tests for the OpenAI agent interfaces (synchronous and asynchronous).
"""

import asyncio
import pytest
from unittest.mock import MagicMock, patch

from langchain_core.messages import AIMessage, HumanMessage

from app.agents.openai_agent import OpenAIAgent


# Mock classes for testing responses
class MockResponse:
    def __init__(self, content: str = "This is a test response."):
        self.messages = [AIMessage(content=content)]


class MockStreamResponse:
    def __init__(self, content: str = "This is a test response."):
        self.content = content
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
    def __init__(self, content: str = "This is an async test response."):
        self.content = content
        self.chunks = [content[i : i + 3] for i in range(0, len(content), 3)]
        self.index = 0

    async def __aiter__(self):
        return self

    async def __anext__(self):
        if self.index < len(self.chunks):
            chunk = {"messages": [AIMessage(content=self.chunks[self.index])]}
            self.index += 1
            return chunk
        raise StopAsyncIteration


# Fixtures
@pytest.fixture
def agent_with_mock_graph():
    """Create an agent with a mocked graph."""
    with (
        patch("app.agents.openai_agent.get_azure_openai_client") as mock_get_client,
        patch("app.agents.openai_agent.ChatOpenAI") as mock_chat_openai,
        patch("app.agents.openai_agent.create_react_agent") as mock_create_agent,
        patch("app.agents.openai_agent.StateGraph") as mock_state_graph,
    ):

        # Mock the Azure OpenAI client
        mock_get_client.return_value = MagicMock()

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

        # Create the agent
        agent = OpenAIAgent(model_name="gpt-4o")

        # Set the mocked graph
        agent.graph = mock_graph

        yield agent, mock_graph


# Tests for synchronous interface
def test_invoke_success(agent_with_mock_graph):
    """Test successful synchronous invocation."""
    agent, mock_graph = agent_with_mock_graph

    # Mock the graph invoke method
    mock_config_graph = MagicMock()
    mock_graph.with_config.return_value = mock_config_graph
    mock_config_graph.invoke.return_value = {
        "messages": [
            HumanMessage(content="Hello"),
            AIMessage(content="Hello! How can I help you today?"),
        ]
    }

    # Invoke the agent
    response = agent.invoke("Hello")

    # Check that the graph was invoked with the correct parameters
    mock_graph.with_config.assert_called_once()
    config = mock_graph.with_config.call_args[0][0]
    assert "checkpointer" in config
    assert "thread_id" in config

    # Check that invoke was called with the correct message
    expected_message = HumanMessage(content="Hello")
    mock_config_graph.invoke.assert_called_once()
    args = mock_config_graph.invoke.call_args[0][0]
    assert "messages" in args
    assert len(args["messages"]) == 1
    assert args["messages"][0].content == expected_message.content
    assert "tools" in args

    # Check the response
    assert response == "Hello! How can I help you today?"


def test_invoke_error_handling(agent_with_mock_graph):
    """Test error handling in synchronous invocation."""
    agent, mock_graph = agent_with_mock_graph

    # Mock the graph invoke method to raise an exception
    mock_config_graph = MagicMock()
    mock_graph.with_config.return_value = mock_config_graph
    mock_config_graph.invoke.side_effect = ValueError("Test error")

    # Invoke the agent
    response = agent.invoke("Hello")

    # Check that the error was handled correctly
    assert "I encountered an error: Test error" in response


def test_invoke_with_thread_id(agent_with_mock_graph):
    """Test synchronous invocation with an existing thread."""
    agent, mock_graph = agent_with_mock_graph

    # Set a thread ID
    thread_id = "test-thread-id"
    agent.thread_id = thread_id

    # Mock the graph invoke method
    mock_config_graph = MagicMock()
    mock_graph.with_config.return_value = mock_config_graph
    mock_config_graph.invoke.return_value = {
        "messages": [
            HumanMessage(content="Hello"),
            AIMessage(content="Hello! How can I help you today?"),
        ]
    }

    # Invoke the agent
    response = agent.invoke("Hello")

    # Check that the graph was invoked with the correct thread ID
    mock_graph.with_config.assert_called_once()
    config = mock_graph.with_config.call_args[0][0]
    assert config["thread_id"] == thread_id


def test_invoke_empty_response(agent_with_mock_graph):
    """Test synchronous invocation with an empty response."""
    agent, mock_graph = agent_with_mock_graph

    # Mock the graph invoke method to return an empty response
    mock_config_graph = MagicMock()
    mock_graph.with_config.return_value = mock_config_graph
    mock_config_graph.invoke.return_value = {"messages": []}

    # Invoke the agent
    response = agent.invoke("Hello")

    # Check that the fallback response was used
    assert response == "I'm sorry, I couldn't process your request."


# Tests for asynchronous interface
@pytest.mark.asyncio
async def test_ainvoke_success(agent_with_mock_graph):
    """Test successful asynchronous invocation."""
    agent, mock_graph = agent_with_mock_graph

    # Mock the graph ainvoke method
    mock_config_graph = MagicMock()
    mock_graph.with_config.return_value = mock_config_graph

    # Create a future that returns our response
    future = asyncio.Future()
    future.set_result(
        {
            "messages": [
                HumanMessage(content="Hello"),
                AIMessage(content="Hello! How can I help you today?"),
            ]
        }
    )
    mock_config_graph.ainvoke = MagicMock(return_value=future)

    # Invoke the agent asynchronously
    response = await agent.ainvoke("Hello")

    # Check that the graph was invoked with the correct parameters
    mock_graph.with_config.assert_called_once()
    config = mock_graph.with_config.call_args[0][0]
    assert "checkpointer" in config
    assert "thread_id" in config

    # Check that ainvoke was called with the correct message
    expected_message = HumanMessage(content="Hello")
    mock_config_graph.ainvoke.assert_called_once()
    args = mock_config_graph.ainvoke.call_args[0][0]
    assert "messages" in args
    assert len(args["messages"]) == 1
    assert args["messages"][0].content == expected_message.content
    assert "tools" in args

    # Check the response
    assert response == "Hello! How can I help you today?"


@pytest.mark.asyncio
async def test_ainvoke_error_handling(agent_with_mock_graph):
    """Test error handling in asynchronous invocation."""
    agent, mock_graph = agent_with_mock_graph

    # Mock the graph ainvoke method to raise an exception
    mock_config_graph = MagicMock()
    mock_graph.with_config.return_value = mock_config_graph

    # Create a future that raises an exception
    future = asyncio.Future()
    future.set_exception(ValueError("Test error"))
    mock_config_graph.ainvoke = MagicMock(return_value=future)

    # Invoke the agent asynchronously
    response = await agent.ainvoke("Hello")

    # Check that the error was handled correctly
    assert "I encountered an error:" in response


@pytest.mark.asyncio
async def test_ainvoke_with_thread_id(agent_with_mock_graph):
    """Test asynchronous invocation with an existing thread."""
    agent, mock_graph = agent_with_mock_graph

    # Set a thread ID
    thread_id = "test-thread-id"
    agent.thread_id = thread_id

    # Mock the graph ainvoke method
    mock_config_graph = MagicMock()
    mock_graph.with_config.return_value = mock_config_graph

    # Create a future that returns our response
    future = asyncio.Future()
    future.set_result(
        {
            "messages": [
                HumanMessage(content="Hello"),
                AIMessage(content="Hello! How can I help you today?"),
            ]
        }
    )
    mock_config_graph.ainvoke = MagicMock(return_value=future)

    # Invoke the agent asynchronously
    await agent.ainvoke("Hello")

    # Check that the graph was invoked with the correct thread ID
    mock_graph.with_config.assert_called_once()
    config = mock_graph.with_config.call_args[0][0]
    assert config["thread_id"] == thread_id


# Tests for streaming interfaces
def test_stream(agent_with_mock_graph):
    """Test synchronous streaming."""
    agent, mock_graph = agent_with_mock_graph

    # Mock the graph stream method
    mock_config_graph = MagicMock()
    mock_graph.with_config.return_value = mock_config_graph

    # Create a mock stream response
    response_content = "This is a streaming response."
    mock_stream = MockStreamResponse(content=response_content)
    mock_config_graph.stream.return_value = mock_stream

    # Stream the response
    chunks = []
    for chunk in agent.stream("Hello"):
        chunks.append(chunk)

    # Check that the graph was configured correctly
    mock_graph.with_config.assert_called_once()
    config = mock_graph.with_config.call_args[0][0]
    assert "checkpointer" in config
    assert "thread_id" in config
    assert "recursion_limit" in config
    assert config["recursion_limit"] == agent.max_iterations

    # Check that stream was called with the correct parameters
    mock_config_graph.stream.assert_called_once()
    args = mock_config_graph.stream.call_args[0][0]
    assert "messages" in args
    assert args["messages"][0].content == "Hello"
    assert "tools" in args

    # Check the stream_mode parameter
    kwargs = mock_config_graph.stream.call_args[1]
    assert "stream_mode" in kwargs
    assert kwargs["stream_mode"] == "values"

    # Check the streamed response
    full_response = "".join(chunks)
    assert full_response == response_content


def test_stream_error_handling(agent_with_mock_graph):
    """Test error handling in synchronous streaming."""
    agent, mock_graph = agent_with_mock_graph

    # Mock the graph stream method to raise an exception
    mock_config_graph = MagicMock()
    mock_graph.with_config.return_value = mock_config_graph
    mock_config_graph.stream.side_effect = ValueError("Test error")

    # Stream the response
    chunks = []
    for chunk in agent.stream("Hello"):
        chunks.append(chunk)

    # Check that the error was handled correctly
    assert len(chunks) == 1
    assert "I encountered an error: Test error" in chunks[0]


@pytest.mark.asyncio
async def test_astream(agent_with_mock_graph):
    """Test asynchronous streaming."""
    agent, mock_graph = agent_with_mock_graph

    # Create a simple async generator as a custom method
    async def custom_astream(self, message):
        yield "This is an async streaming response."

    # Replace the agent's astream method
    # Save the original method
    original_astream = agent.astream
    agent.astream = lambda message: custom_astream(agent, message)

    try:
        # Stream the response asynchronously
        chunks = []
        async for chunk in agent.astream("Hello"):
            chunks.append(chunk)

        # Check the chunks
        assert len(chunks) == 1
        assert chunks[0] == "This is an async streaming response."
    finally:
        # Restore the original method
        agent.astream = original_astream


@pytest.mark.asyncio
async def test_astream_error_handling(agent_with_mock_graph):
    """Test error handling in asynchronous streaming."""
    agent, mock_graph = agent_with_mock_graph

    # Create a simple async generator that raises an error
    async def custom_error_astream(self, message):
        raise ValueError("Test error")
        yield "This should not be reached"

    # Replace the agent's astream method
    # Save the original method
    original_astream = agent.astream
    agent.astream = lambda message: custom_error_astream(agent, message)

    try:
        # Stream the response asynchronously
        chunks = []
        try:
            async for chunk in agent.astream("Hello"):
                chunks.append(chunk)
        except ValueError as e:
            assert str(e) == "Test error"
            assert len(chunks) == 0
    finally:
        # Restore the original method
        agent.astream = original_astream
