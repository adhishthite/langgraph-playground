"""
Demo script for the basic OpenAI agent.

This script showcases the functionality of the OpenAI agent
with different models and interaction patterns.
"""

import asyncio
import logging
from typing import List

from langchain_core.tools import BaseTool, tool
from app.agents import OpenAIAgent, create_default_agent

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("agent_demo")


@tool
def weather(location: str) -> str:
    """
    Get the current weather for a location.
    Note: This is a mock implementation for demonstration purposes.

    Args:
        location: The location to get weather for

    Returns:
        The current weather for the location
    """
    # This is just a mock implementation
    weathers = {
        "new york": "72°F, Partly Cloudy",
        "london": "65°F, Rainy",
        "tokyo": "80°F, Sunny",
        "sydney": "70°F, Clear",
        "paris": "68°F, Overcast",
    }

    location = location.lower()
    if location in weathers:
        return f"The current weather in {location.title()} is {weathers[location]}."
    else:
        return f"Weather information for {location} is not available."


@tool
def search(query: str) -> str:
    """
    Search for information on the web.
    Note: This is a mock implementation for demonstration purposes.

    Args:
        query: The search query

    Returns:
        The search results
    """
    # Mock search results
    return (
        f"Here are the top search results for '{query}':\n"
        f"1. Example result 1 for {query}\n"
        f"2. Example result 2 for {query}\n"
        f"3. Example result 3 for {query}"
    )


def create_demo_agent(model_name: str = "gpt-4o") -> OpenAIAgent:
    """
    Create a demo agent with custom tools.

    Args:
        model_name: The model to use

    Returns:
        An OpenAI agent instance
    """
    # Create custom tools
    tools: List[BaseTool] = [weather, search]

    # Create a system prompt
    system_prompt = """You are a helpful AI assistant with access to tools.
    
You can help the user by answering questions and using tools when necessary.

When using the weather tool, be sure to extract the location from the user's query.
When using the search tool, be sure to extract relevant search terms from the user's query.
    """

    # Create and return the agent
    return OpenAIAgent(
        model_name=model_name,
        temperature=0.7,
        system_prompt=system_prompt,
        tools=tools,
    )


async def run_async_demo() -> None:
    """Run an asynchronous demo with streaming."""
    logger.info("Starting asynchronous demo")

    # Create a demo agent
    agent = create_demo_agent(model_name="gpt-4o-mini")

    # List of user messages to demonstrate
    messages = [
        "What's the weather like in London?",
        "Can you search for information about LangGraph?",
        "Calculate 156 * 42",
    ]

    for message in messages:
        logger.info(f"User: {message}")

        # Stream the response
        logger.info("Agent (streaming): ")
        response_chunks = []
        async for chunk in agent.astream(message):
            print(chunk, end="", flush=True)
            response_chunks.append(chunk)
        print()  # Add a newline

        # Get the complete response
        full_response = "".join(response_chunks)
        logger.info(f"Complete response: {full_response}")
        print("-" * 50)


def run_sync_demo() -> None:
    """Run a synchronous demo."""
    logger.info("Starting synchronous demo")

    # Create a demo agent
    agent = create_default_agent(model_name="gpt-4o")

    # List of user messages to demonstrate
    messages = [
        "What time is it?",
        "Calculate 25 squared plus 13",
        "Tell me a joke about programming",
    ]

    for message in messages:
        logger.info(f"User: {message}")

        # Get the response
        response = agent.invoke(message)
        logger.info(f"Agent: {response}")
        print("-" * 50)


if __name__ == "__main__":
    # Run the synchronous demo
    run_sync_demo()

    # Run the asynchronous demo
    asyncio.run(run_async_demo())
