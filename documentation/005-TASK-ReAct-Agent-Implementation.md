# 005-TASK: ReAct Agent Implementation

## Overview
Implement a ReAct agent using LangGraph's functional API to create a flexible, stateful agent capable of using tools and maintaining conversational context.

## Requirements
- Implement a ReAct agent using LangGraph's functional API
- Create a stateful agent with memory persistence
- Support multiple tools integration
- Implement proper conversation context management
- Support LangSmith tracing for observability
- Create configurable system prompt

## Implementation Details

### Agent Module
Create `app/agents/openai_agents.py` with the following features:

```python
# Example implementation
import uuid
from typing import Dict, Any, List, Optional, TypedDict, Annotated
from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, FunctionMessage
from langchain_core.prompts import MessagesPlaceholder

from langgraph.func import entrypoint, task
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, State, Command

from app.config.settings import settings
from app.core.llm_clients import get_model
from app.tools.date_tool import get_current_date, calculate_date_difference
from app.tools.webscraper_tool import scrape_webpage, extract_links

# Define state schema using TypedDict
class AgentState(TypedDict):
    messages: List[Dict[str, Any]]  # Conversation messages
    current_tool_calls: Optional[List[Dict[str, Any]]]  # Tool calls to be executed
    tool_results: Optional[List[Dict[str, Any]]]  # Results from executed tools
    waiting_for_user: bool  # Flag indicating if waiting for user input
    user_response: Optional[Any]  # User response when agent is waiting
    metadata: Dict[str, Any]  # Additional metadata

# Tools configuration
def get_tools():
    """Get the list of available tools."""
    return [
        get_current_date,
        calculate_date_difference,
        scrape_webpage,
        extract_links,
    ]

# Model task for generating responses
@task
async def generate_assistant_response(state: AgentState) -> AgentState:
    """Generate an assistant response using the model."""
    # Prepare model with tools
    model = get_model(
        model_name="gpt-4o",
        temperature=0.2,
        streaming=True,
    )
    
    tools = get_tools()
    
    # Process messages for the model
    messages = [
        SystemMessage(content=state["metadata"].get("system_prompt", DEFAULT_SYSTEM_PROMPT)),
    ]
    
    # Add conversation history
    messages.extend(state["messages"])
    
    # Generate response with tool calling
    response = await model.ainvoke(
        messages,
        tools=[tool.to_openai_tool() for tool in tools],
    )
    
    # Update state with new message
    state["messages"].append(response)
    
    # Check for tool calls
    if hasattr(response, "tool_calls") and response.tool_calls:
        state["current_tool_calls"] = response.tool_calls
    else:
        state["current_tool_calls"] = None
        
    return state

# Task for executing tools
@task
async def execute_tools(state: AgentState) -> AgentState:
    """Execute tool calls from the assistant."""
    if not state["current_tool_calls"]:
        # No tools to execute
        return state
        
    tool_results = []
    tools = {tool.__name__: tool for tool in get_tools()}
    
    # Execute each tool call
    for tool_call in state["current_tool_calls"]:
        tool_name = tool_call["name"]
        tool_args = tool_call["arguments"]
        
        if tool_name in tools:
            try:
                # Execute the tool
                tool_fn = tools[tool_name]
                result = await tool_fn.ainvoke(tool_args)
                
                # Add result to the state
                tool_results.append({
                    "tool_call_id": tool_call["id"],
                    "name": tool_name,
                    "result": result
                })
            except Exception as e:
                # Handle tool execution errors
                tool_results.append({
                    "tool_call_id": tool_call["id"],
                    "name": tool_name,
                    "error": str(e)
                })
    
    # Update state with tool results
    state["tool_results"] = tool_results
    
    # Add tool results as messages
    for result in tool_results:
        state["messages"].append(
            FunctionMessage(
                content=str(result["result"]) if "result" in result else str(result["error"]),
                name=result["name"],
                tool_call_id=result["tool_call_id"]
            )
        )
    
    # Clear current tool calls
    state["current_tool_calls"] = None
    
    return state

# Task for determining next step
@task
def decide_next(state: AgentState) -> str:
    """Decide the next step in the graph."""
    # If waiting for user, return to wait node
    if state.get("waiting_for_user", False):
        return "wait_for_user"
    
    # If there are tool calls, execute tools
    if state.get("current_tool_calls"):
        return "execute_tools"
        
    # Default to assistant response
    return "assistant"

# Task for waiting on user input
@task
def wait_for_user(state: AgentState) -> AgentState:
    """Wait for user input."""
    # Use interrupt to pause execution and wait for user
    user_response = interrupt({
        "messages": state["messages"],
        "waiting_for": "user_input"
    })
    
    # When execution resumes, add user response to messages
    state["messages"].append(HumanMessage(content=user_response))
    state["waiting_for_user"] = False
    state["user_response"] = None
    
    return state

# Default system prompt
DEFAULT_SYSTEM_PROMPT = """
You are a helpful assistant with access to various tools.
Use the tools when needed to provide accurate and helpful responses.
Always think step-by-step and explain your reasoning.
"""

# Main agent entrypoint
@entrypoint(checkpointer=MemorySaver())
async def react_agent(
    message: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    A ReAct agent that can use tools and maintain conversational context.
    
    Args:
        message: The user's message
        metadata: Additional metadata for configuration
        
    Returns:
        The updated agent state
    """
    # Initialize state
    state: AgentState = {
        "messages": [HumanMessage(content=message)],
        "current_tool_calls": None,
        "tool_results": None,
        "waiting_for_user": False,
        "user_response": None,
        "metadata": metadata or {}
    }

    # Define the workflow using task composition
    while True:
        # Generate assistant response
        state = await generate_assistant_response(state)
        
        # Decide next steps
        next_step = decide_next(state)
        
        # Execute appropriate step
        if next_step == "execute_tools":
            state = await execute_tools(state)
        elif next_step == "wait_for_user":
            state = wait_for_user(state)
        else:  # assistant or any other state
            break
    
    # Return final state
    return {
        "messages": state["messages"],
        "metadata": state["metadata"],
    }
```

### Integration with Configuration
- Ensure agent uses models and settings from configuration
- Allow customization of system prompt
- Enable LangSmith tracing for better observability

## Success Criteria
- ReAct agent implementation works with provided tools
- Agent maintains conversation context across interactions
- Memory persistence works correctly with thread IDs
- LangSmith tracing provides visibility into agent execution
- Agent can be configured with different system prompts and models
- Agent correctly handles tool execution and errors