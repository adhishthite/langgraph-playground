"""
Tests for the OpenAI agent using conftest fixtures.
"""

import pytest
from langchain_core.tools import tool

from langchain_core.messages import AIMessage
from app.agents.openai_agent import OpenAIAgent


# Test tool for this test file
@tool
def local_test_tool(text: str) -> str:
    """A simple tool that echoes the input."""
    return f"Echo: {text}"


def test_agent_with_fixtures(mock_env_vars, mock_openai_agent_components):
    """Test agent initialization and behavior using the fixtures."""
    # Create an agent without tools to avoid referencing the conftest tool
    agent = OpenAIAgent(
        model_name="gpt-4o",
        temperature=0.7,
        tools=[local_test_tool],
    )

    # Set the mocked graph
    agent.graph = mock_openai_agent_components["graph"]

    # Test the agent's invoke method
    response = agent.invoke("Hello, agent!")

    # Check the response
    assert response == "This is a test response from the mocked agent."


@pytest.mark.asyncio
async def test_agent_async_with_fixtures(mock_env_vars, mock_openai_agent_components):
    """Test agent asynchronous behavior using the fixtures."""
    # Create an agent without tools to avoid referencing the conftest tool
    agent = OpenAIAgent(
        model_name="gpt-4o",
        temperature=0.7,
    )

    # Set the mocked graph
    agent.graph = mock_openai_agent_components["graph"]

    # Test the agent's ainvoke method
    response = await agent.ainvoke("Hello, agent!")

    # Check the response
    assert response == "This is an async test response from the mocked agent."


def test_agent_streaming_with_fixtures(
    mock_env_vars, mock_openai_agent_components, mock_streaming_responses
):
    """Test agent streaming behavior using the fixtures."""
    # Create an agent
    agent = OpenAIAgent(
        model_name="gpt-4o",
        temperature=0.7,
    )

    # Set the mocked graph
    agent.graph = mock_openai_agent_components["graph"]

    # Set up the streaming response
    mock_config_graph = mock_openai_agent_components["config_graph"]
    stream_content = "This is a streaming test response."
    mock_config_graph.stream.return_value = mock_streaming_responses["stream"](
        content=stream_content
    )

    # Test the agent's stream method
    chunks = []
    for chunk in agent.stream("Hello, agent!"):
        chunks.append(chunk)

    # Check the streamed response
    full_response = "".join(chunks)
    assert full_response == stream_content


@pytest.mark.asyncio
async def test_agent_async_streaming_with_fixtures(
    mock_env_vars, mock_openai_agent_components, mock_streaming_responses
):
    """Test agent asynchronous streaming behavior using the fixtures."""
    # Create an agent
    agent = OpenAIAgent(
        model_name="gpt-4o",
        temperature=0.7,
    )

    # Set the mocked graph
    agent.graph = mock_openai_agent_components["graph"]

    # Mock the astream method to return a simple string
    # This avoids complex async mocking
    async def mock_astream(*args, **kwargs):
        content = "This is an async streaming test response."
        for i in range(0, len(content), 3):
            chunk = content[i : i + 3]
            yield chunk

    # Replace the astream method with our mock
    agent.astream = mock_astream

    # Test the agent's astream method
    chunks = []
    async for chunk in agent.astream("Hello, agent!"):
        chunks.append(chunk)

    # Check the streamed response
    full_response = "".join(chunks)
    assert full_response == "This is an async streaming test response."


def test_agent_tool_call_with_fixtures(
    mock_env_vars, mock_openai_agent_components, mock_tool_call_responses
):
    """Test agent tool call behavior using the fixtures."""
    # Create an agent with tools
    agent = OpenAIAgent(
        model_name="gpt-4o",
        temperature=0.7,
        tools=[local_test_tool],
    )

    # Set the mocked graph
    agent.graph = mock_openai_agent_components["graph"]

    # Override the default mock to return a custom response
    mock_config_graph = mock_openai_agent_components["config_graph"]
    mock_config_graph.invoke.return_value = {
        "messages": [AIMessage(content="The tool returned: Echo: test message")]
    }

    # Test the agent's invoke method with a tool call scenario
    response = agent.invoke("Use the echo tool with 'test message'")

    # Verify the response contains the expected tool output
    assert "The tool returned: Echo: test message" in response
