"""
Basic OpenAI agent implementation using LangGraph.

This module provides a simple, direct OpenAI agent that uses the ReAct pattern
for reasoning and acting. It supports both GPT-4o and GPT-4o-mini models.
"""

import logging
import uuid
from typing import Any, List, Optional, TypedDict, Annotated

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
)
from langchain_core.tools import BaseTool, tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
import operator  # Required for Annotated type

from app.client.azure_openai_client import get_azure_openai_client
from app.config import azure_openai_settings

# Set up logging
logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State for the OpenAI ReAct Agent."""

    messages: List[BaseMessage]
    """Chat history of the conversation."""

    tools: List[BaseTool]
    """Tools available to the agent."""


class SystemPromptTemplate:
    """System prompt templates for different agent types."""

    DEFAULT = """You are a helpful AI assistant. 
    
You can help the user with various tasks and answer questions to the best of your ability.

When you need more information or need to perform a specific action, use the tools available to you.
"""

    @staticmethod
    def format(template: str, **kwargs: Any) -> str:
        """
        Format a system prompt template with the given parameters.

        Args:
            template: The template string to format
            **kwargs: Parameters to substitute into the template

        Returns:
            The formatted template string
        """
        return template.format(**kwargs)


class OpenAIAgent:
    """
    Basic OpenAI agent implementation using LangGraph.

    This agent uses the ReAct pattern to reason and act based on available tools.
    It supports both synchronous and asynchronous interfaces.
    """

    def __init__(
        self,
        model_name: str = "gpt-4o",
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
        tools: Optional[List[BaseTool]] = None,
        max_iterations: int = 10,
    ):
        """
        Initialize the OpenAI agent.

        Args:
            model_name: The model to use (gpt-4o or gpt-4o-mini)
            temperature: The temperature for generation
            system_prompt: Custom system prompt (uses default if None)
            tools: List of tools available to the agent
            max_iterations: Maximum number of agent think-act iterations
        """
        self.model_name = model_name
        self.temperature = temperature
        self.system_prompt = system_prompt or SystemPromptTemplate.DEFAULT
        self.tools = tools or []
        self.max_iterations = max_iterations
        self.thread_id = None
        self.checkpointer = MemorySaver()

        # Initialize the LLM client
        self._init_llm()

        # Build the agent graph
        self._build_agent_graph()

    def _init_llm(self) -> None:
        """Initialize the LLM client for the agent."""
        # Get the Azure OpenAI client
        azure_client = get_azure_openai_client()
        if not azure_client:
            raise ValueError("Azure OpenAI client initialization failed")

        # Create the ChatOpenAI instance using Azure client
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            azure_openai_api_key=azure_openai_settings.api_key,
            azure_endpoint=azure_openai_settings.endpoint,
            api_version=azure_openai_settings.api_version,
            streaming=True,
            model_kwargs={"response_format": {"type": "text"}},
        )

    def _build_agent_graph(self) -> None:
        """Build the ReAct agent graph using LangGraph."""
        # Create the ReAct agent
        self.agent_runnable = create_react_agent(
            self.llm,
            self.tools,
            system_prompt=self.system_prompt,
        )

        # Define agent state
        class AgentState(TypedDict):
            messages: Annotated[List[BaseMessage], operator.add]
            tools: List[BaseTool]

        # Create the graph
        builder = StateGraph(AgentState)

        # Add agent node
        builder.add_node("agent", self.agent_runnable)

        # Define edges
        builder.set_entry_point("agent")
        builder.add_conditional_edges(
            "agent",
            lambda state: "tool" if state.get("tool_calls") else END,
            {
                "tool": "agent",
                END: END,
            },
        )

        # Compile the graph
        self.graph = builder.compile()

    def create_thread(self) -> str:
        """
        Create a new thread for the conversation.

        Returns:
            The thread ID
        """
        self.thread_id = str(uuid.uuid4())
        return self.thread_id

    def get_thread_id(self) -> Optional[str]:
        """
        Get the current thread ID.

        Returns:
            The thread ID or None if no thread exists
        """
        return self.thread_id

    def invoke(self, message: str) -> str:
        """
        Invoke the agent synchronously with a user message.

        Args:
            message: The user message

        Returns:
            The agent's response
        """
        # Create a thread if it doesn't exist
        if not self.thread_id:
            self.create_thread()

        # Create input state
        human_message = HumanMessage(content=message)

        # Get checkpoint if it exists
        events = None
        try:
            events = self.graph.with_config(
                {"checkpointer": self.checkpointer, "thread_id": self.thread_id}
            ).invoke({"messages": [human_message], "tools": self.tools})
        except Exception as e:
            logger.error(f"Error invoking agent: {e}")
            return f"I encountered an error: {str(e)}"

        # Extract the agent response
        if events and isinstance(events, dict) and "messages" in events:
            messages = events["messages"]
            if messages and len(messages) > 0:
                return messages[-1].content

        return "I'm sorry, I couldn't process your request."

    async def ainvoke(self, message: str) -> str:
        """
        Invoke the agent asynchronously with a user message.

        Args:
            message: The user message

        Returns:
            The agent's response
        """
        # Create a thread if it doesn't exist
        if not self.thread_id:
            self.create_thread()

        # Create input state
        human_message = HumanMessage(content=message)

        # Get checkpoint if it exists
        events = None
        try:
            events = await self.graph.with_config(
                {"checkpointer": self.checkpointer, "thread_id": self.thread_id}
            ).ainvoke({"messages": [human_message], "tools": self.tools})
        except Exception as e:
            logger.error(f"Error invoking agent asynchronously: {e}")
            return f"I encountered an error: {str(e)}"

        # Extract the agent response
        if events and isinstance(events, dict) and "messages" in events:
            messages = events["messages"]
            if messages and len(messages) > 0:
                return messages[-1].content

        return "I'm sorry, I couldn't process your request."

    def stream(self, message: str):
        """
        Stream the agent's response to a user message.

        Args:
            message: The user message

        Yields:
            Chunks of the agent's response
        """
        # Create a thread if it doesn't exist
        if not self.thread_id:
            self.create_thread()

        # Create input state
        human_message = HumanMessage(content=message)

        try:
            # Stream responses
            for chunk in self.graph.with_config(
                {
                    "checkpointer": self.checkpointer,
                    "thread_id": self.thread_id,
                    "recursion_limit": self.max_iterations,
                }
            ).stream(
                {"messages": [human_message], "tools": self.tools},
                stream_mode="values",
            ):
                if "messages" in chunk and chunk["messages"]:
                    latest_message = chunk["messages"][-1]
                    if isinstance(latest_message, AIMessage) and latest_message.content:
                        yield latest_message.content
        except Exception as e:
            logger.error(f"Error streaming agent response: {e}")
            yield f"I encountered an error: {str(e)}"

    async def astream(self, message: str):
        """
        Stream the agent's response asynchronously to a user message.

        Args:
            message: The user message

        Yields:
            Chunks of the agent's response
        """
        # Create a thread if it doesn't exist
        if not self.thread_id:
            self.create_thread()

        # Create input state
        human_message = HumanMessage(content=message)

        try:
            # Stream responses asynchronously
            async for chunk in self.graph.with_config(
                {
                    "checkpointer": self.checkpointer,
                    "thread_id": self.thread_id,
                    "recursion_limit": self.max_iterations,
                }
            ).astream(
                {"messages": [human_message], "tools": self.tools},
                stream_mode="values",
            ):
                if "messages" in chunk and chunk["messages"]:
                    latest_message = chunk["messages"][-1]
                    if isinstance(latest_message, AIMessage) and latest_message.content:
                        yield latest_message.content
        except Exception as e:
            logger.error(f"Error streaming agent response asynchronously: {e}")
            yield f"I encountered an error: {str(e)}"


# Example tool implementation
@tool
def calculator(expression: str) -> str:
    """
    Calculate the result of a mathematical expression.

    Args:
        expression: The mathematical expression to calculate

    Returns:
        The result of the calculation
    """
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error calculating expression: {str(e)}"


# Helper function to create an OpenAI agent with default tools
def create_default_agent(
    model_name: str = "gpt-4o",
    temperature: float = 0.7,
    system_prompt: Optional[str] = None,
) -> OpenAIAgent:
    """
    Create an OpenAI agent with default tools.

    Args:
        model_name: The model to use (gpt-4o or gpt-4o-mini)
        temperature: The temperature for generation
        system_prompt: Custom system prompt

    Returns:
        OpenAI agent instance
    """
    # Create default tools
    tools = [calculator]

    # Create and return the agent
    return OpenAIAgent(
        model_name=model_name,
        temperature=temperature,
        system_prompt=system_prompt,
        tools=tools,
    )
