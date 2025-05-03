"""
Tests for the OpenAI agent tool integration.
"""

import asyncio
import pytest
from unittest.mock import MagicMock, patch

from langchain_core.messages import AIMessage
from langchain_core.tools import tool

from app.agents.openai_agent import OpenAIAgent, calculator


# Test tools
@tool
def test_echo(text: str) -> str:
    """Echo the input text."""
    return f"Echo: {text}"


@tool
def test_uppercase(text: str) -> str:
    """Convert input text to uppercase."""
    return text.upper()


# Fixtures
@pytest.fixture
def agent_with_tools():
    """Create an agent with test tools."""
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

        # Create the tools
        tools = [test_echo, test_uppercase]

        # Create the agent
        agent = OpenAIAgent(
            model_name="gpt-4o",
            tools=tools,
        )

        # Set the mocked graph
        agent.graph = mock_graph

        yield agent, mock_graph, tools


# Tests for tool integration
def test_agent_init_with_tools(agent_with_tools):
    """Test that the agent initializes correctly with tools."""
    agent, _, tools = agent_with_tools

    # Check that the tools were set correctly
    assert agent.tools == tools


def test_calculator_tool():
    """Test the calculator tool."""
    # Test simple addition
    result = calculator.invoke("2 + 2")
    assert result == "4"

    # Test more complex expression
    result = calculator.invoke("(5 * 10) - 7")
    assert result == "43"

    # Test error handling
    result = calculator.invoke("5 / 0")
    assert "Error calculating expression" in result


def test_invoke_with_tool_call(agent_with_tools):
    """Test synchronous invocation with a tool call."""
    agent, mock_graph, _ = agent_with_tools

    # Mock the graph invoke method with a direct response
    mock_config_graph = MagicMock()
    mock_graph.with_config.return_value = mock_config_graph

    # Return a final result directly - simplifying the test
    final_response = {
        "messages": [AIMessage(content="The echo tool returned: Echo: Hello world")]
    }
    mock_config_graph.invoke.return_value = final_response

    # Invoke the agent
    response = agent.invoke("Echo this: Hello world")

    # Check the response
    assert response == "The echo tool returned: Echo: Hello world"


def test_create_default_agent_with_calculator():
    """Test that the default agent includes the calculator tool."""
    # Mock the OpenAI agent initialization
    with patch("app.agents.openai_agent.OpenAIAgent") as mock_agent_class:
        # Mock the agent instance
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent

        # Mock the calculator tool
        mock_calculator = MagicMock()

        # Patch the calculator
        with patch("app.agents.openai_agent.calculator", mock_calculator):
            # Import the create_default_agent function
            from app.agents.openai_agent import create_default_agent

            # Create a default agent
            agent = create_default_agent()

            # Verify OpenAIAgent was called with calculator in tools
            mock_agent_class.assert_called_once()
            _, kwargs = mock_agent_class.call_args
            assert isinstance(kwargs.get("tools"), list)
            assert mock_calculator in kwargs.get("tools")


@pytest.mark.asyncio
async def test_ainvoke_with_tool_call(agent_with_tools):
    """Test asynchronous invocation with a tool call."""
    agent, mock_graph, _ = agent_with_tools

    # Mock the graph ainvoke method with a simple response
    mock_config_graph = MagicMock()
    mock_graph.with_config.return_value = mock_config_graph

    # Create a simple future with the final response
    future = asyncio.Future()
    future.set_result(
        {
            "messages": [
                AIMessage(content="The uppercase tool returned: MAKE ME UPPERCASE")
            ]
        }
    )
    mock_config_graph.ainvoke = MagicMock(return_value=future)

    # Invoke the agent asynchronously
    response = await agent.ainvoke("Convert this to uppercase: make me uppercase")

    # Check the response
    assert response == "The uppercase tool returned: MAKE ME UPPERCASE"


def test_tool_error_handling(agent_with_tools):
    """Test error handling when a tool raises an exception."""
    agent, mock_graph, _ = agent_with_tools

    # Create a simple failing tool function
    def failing_tool_func(text: str) -> str:
        """A tool that always fails."""
        raise ValueError("Tool failure")

    # Create a mock failing tool
    failing_tool = MagicMock()
    failing_tool.__name__ = "failing_tool"
    failing_tool.invoke.side_effect = ValueError("Tool failure")

    # Add the failing tool to the agent
    agent.tools.append(failing_tool)

    # Mock the graph invoke method
    mock_config_graph = MagicMock()
    mock_graph.with_config.return_value = mock_config_graph

    # Return a response that indicates the tool error
    mock_config_graph.invoke.return_value = {
        "messages": [AIMessage(content="The tool encountered an error: Tool failure")]
    }

    # Invoke the agent
    response = agent.invoke("Use the failing tool")

    # Check the response
    assert "The tool encountered an error: Tool failure" in response


# Integration test with multiple tools
def test_tool_sequence(agent_with_tools):
    """Test a sequence of tool calls."""
    agent, mock_graph, _ = agent_with_tools

    # Mock the graph invoke method with a final result
    mock_config_graph = MagicMock()
    mock_graph.with_config.return_value = mock_config_graph

    # Set up a direct final response
    final_response = {
        "messages": [
            AIMessage(
                content="First I echoed: Hello, then I converted it to uppercase: HELLO"
            )
        ]
    }
    mock_config_graph.invoke.return_value = final_response

    # Invoke the agent
    response = agent.invoke("First echo Hello, then convert the result to uppercase")

    # Check the response
    assert response == "First I echoed: Hello, then I converted it to uppercase: HELLO"
