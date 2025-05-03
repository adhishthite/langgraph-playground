"""
Tests for the OpenAI agent implementation.
"""

from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.tools import tool

from app.agents.openai_agent import (
    OpenAIAgent,
    SystemPromptTemplate,
    create_default_agent,
)


# Test tool for the agent tests
@tool
def test_tool(input_text: str) -> str:
    """A simple test tool that echoes the input."""
    return f"Tool received: {input_text}"


# Mock classes and helper functions
class MockChatCompletion:
    def __init__(self, content: str, tool_calls: Optional[List[Dict[str, Any]]] = None):
        self.choices = [
            MagicMock(
                message=MagicMock(
                    role="assistant", content=content, tool_calls=tool_calls or []
                )
            )
        ]


class MockStreamingChatCompletion:
    def __init__(self, content: str):
        # Split content into chunks for streaming
        chunks = [content[i : i + 3] for i in range(0, len(content), 3)]
        self.chunks = chunks
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current < len(self.chunks):
            chunk = self.chunks[self.current]
            self.current += 1
            mock_chunk = MagicMock()
            mock_chunk.choices = [MagicMock(delta=MagicMock(content=chunk))]
            return mock_chunk
        raise StopIteration


# Tests for agent initialization
def test_agent_initialization():
    """Test that the agent initializes correctly."""
    # Mock the Azure OpenAI client
    with (
        patch("app.agents.openai_agent.get_azure_openai_client") as mock_get_client,
        patch("app.agents.openai_agent.ChatOpenAI") as mock_chat_openai,
        patch("app.agents.openai_agent.create_react_agent") as mock_create_agent,
        patch("app.agents.openai_agent.StateGraph") as mock_state_graph,
    ):

        # Mock the Azure OpenAI client
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Create an agent
        agent = OpenAIAgent(
            model_name="gpt-4o",
            temperature=0.7,
        )

        # Check that the agent was initialized correctly
        assert agent.model_name == "gpt-4o"
        assert agent.temperature == 0.7
        assert agent.system_prompt == SystemPromptTemplate.DEFAULT
        assert agent.tools == []
        assert agent.max_iterations == 10
        assert agent.thread_id is None

        # Check that the Azure OpenAI client was initialized
        mock_get_client.assert_called_once()

        # Check that ChatOpenAI was initialized with the correct parameters
        mock_chat_openai.assert_called_once()

        # Check that the LangGraph components were initialized
        mock_create_agent.assert_called_once()
        mock_state_graph.assert_called_once()


def test_agent_initialization_with_tools():
    """Test that the agent initializes correctly with tools."""
    # Create tools
    tools = [test_tool]

    # Mock the dependencies
    with (
        patch("app.agents.openai_agent.get_azure_openai_client") as mock_get_client,
        patch("app.agents.openai_agent.ChatOpenAI") as mock_chat_openai,
        patch("app.agents.openai_agent.create_react_agent") as mock_create_agent,
        patch("app.agents.openai_agent.StateGraph"),
    ):

        # Mock the Azure OpenAI client
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Create an agent with the tools
        agent = OpenAIAgent(
            model_name="gpt-4o",
            temperature=0.7,
            tools=tools,
        )

        # Check that the tools were set correctly
        assert agent.tools == tools

        # Check that create_react_agent was called with the tools
        mock_create_agent.assert_called_once()
        args, kwargs = mock_create_agent.call_args
        assert kwargs.get("system_prompt") == SystemPromptTemplate.DEFAULT
        assert len(args) >= 2 and args[1] == tools


def test_agent_initialization_with_custom_system_prompt():
    """Test that the agent initializes correctly with a custom system prompt."""
    # Create a custom system prompt
    custom_prompt = "You are a test assistant."

    # Mock the dependencies
    with (
        patch("app.agents.openai_agent.get_azure_openai_client") as mock_get_client,
        patch("app.agents.openai_agent.ChatOpenAI") as mock_chat_openai,
        patch("app.agents.openai_agent.create_react_agent") as mock_create_agent,
        patch("app.agents.openai_agent.StateGraph"),
    ):

        # Mock the Azure OpenAI client
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Create an agent with the custom prompt
        agent = OpenAIAgent(
            model_name="gpt-4o",
            temperature=0.7,
            system_prompt=custom_prompt,
        )

        # Check that the system prompt was set correctly
        assert agent.system_prompt == custom_prompt

        # Check that create_react_agent was called with the custom prompt
        mock_create_agent.assert_called_once()
        args, kwargs = mock_create_agent.call_args
        assert kwargs.get("system_prompt") == custom_prompt


def test_agent_initialization_with_invalid_client():
    """Test that the agent initialization fails with an invalid client."""
    # Mock the Azure OpenAI client to return None
    with patch("app.agents.openai_agent.get_azure_openai_client") as mock_get_client:
        mock_get_client.return_value = None

        # Check that creating an agent raises a ValueError
        with pytest.raises(ValueError) as excinfo:
            OpenAIAgent(
                model_name="gpt-4o",
                temperature=0.7,
            )

        # Check the error message
        assert "Azure OpenAI client initialization failed" in str(excinfo.value)


def test_create_default_agent():
    """Test the create_default_agent helper function."""
    # Mock the dependencies
    with (
        patch("app.agents.openai_agent.calculator") as mock_calculator,
        patch("app.agents.openai_agent.OpenAIAgent") as mock_agent_class,
    ):

        # Set up the mock calculator tool
        mock_calculator.__name__ = "calculator"

        # Create a mock agent instance
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent

        # Create a default agent
        agent = create_default_agent(
            model_name="gpt-4o",
            temperature=0.7,
        )

        # Check that OpenAIAgent was called with the correct parameters
        mock_agent_class.assert_called_once()
        _, kwargs = mock_agent_class.call_args
        assert kwargs.get("model_name") == "gpt-4o"
        assert kwargs.get("temperature") == 0.7
        assert isinstance(kwargs.get("tools"), list)

        # Check that the agent has the calculator tool
        tools = kwargs.get("tools")
        assert len(tools) == 1
        # Just check that the calculator is in the tools list without checking the name
        assert mock_calculator in tools

        # Check that the agent was returned
        assert agent == mock_agent


def test_system_prompt_template_format():
    """Test the SystemPromptTemplate format method."""
    # Create a template with placeholders
    template = "Hello {name}! You are a {role}."

    # Format the template
    formatted = SystemPromptTemplate.format(template, name="Test", role="assistant")

    # Check that the template was formatted correctly
    assert formatted == "Hello Test! You are a assistant."


def test_agent_create_thread():
    """Test the create_thread method."""
    # Mock UUID generation
    with (
        patch("app.agents.openai_agent.get_azure_openai_client") as mock_get_client,
        patch("app.agents.openai_agent.ChatOpenAI"),
        patch("app.agents.openai_agent.create_react_agent"),
        patch("app.agents.openai_agent.StateGraph"),
        patch("app.agents.openai_agent.uuid.uuid4") as mock_uuid,
    ):

        # Mock the UUID to return a string directly
        mock_uuid.return_value = "test-uuid"

        # Mock the Azure OpenAI client
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Create the agent
        agent = OpenAIAgent()

        # Create a thread
        thread_id = agent.create_thread()

        # Check that the thread ID was set correctly
        assert thread_id == "test-uuid"
        assert agent.thread_id == "test-uuid"
