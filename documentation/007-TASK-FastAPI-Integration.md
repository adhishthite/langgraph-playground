# 007-TASK: FastAPI Integration

## Overview
Create a FastAPI application that exposes the LangGraph agents as API endpoints with streaming support and proper error handling.

## Requirements
- Implement FastAPI application structure
- Create unified endpoint for all agents
- Support Server-Sent Events (SSE) for streaming
- Implement proper request validation
- Add error handling and logging
- Include health check endpoints

## Implementation Details

### API Module Structure
Create the FastAPI application structure in the following files:
- `app/main.py` - Main FastAPI application entry point
- `app/api/routes.py` - API routes for agents and health checks
- `app/streaming/agent_streaming.py` - Streaming infrastructure

### Main Application Entry Point
Create `app/main.py`:

```python
# Example implementation
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.config.settings import settings

# Create FastAPI application
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    debug=settings.API_DEBUG,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api")

# Error handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    # Log the error
    import traceback
    traceback.print_exc()
    
    # Return error response
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "detail": "An internal server error occurred"},
    )

# Entry point for running the application
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.API_DEBUG)
```

### API Routes
Create `app/api/routes.py`:

```python
# Example implementation
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.core.registry import agent_registry
from app.streaming.agent_streaming import stream_agent_events
from app.config.settings import settings

# Create router
router = APIRouter()

# Request models
class AgentRequest(BaseModel):
    """Request model for agent interactions."""
    message: str = Field(..., description="User message to the agent")
    agent: str = Field("react", description="Agent type to use")
    thread_id: Optional[str] = Field(None, description="Thread ID for conversation persistence")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the agent")

# Response models
class AgentResponse(BaseModel):
    """Response model for non-streaming agent interactions."""
    messages: list = Field(..., description="List of conversation messages")
    thread_id: str = Field(..., description="Thread ID for conversation persistence")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata from the agent")

# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

# List available agents endpoint
@router.get("/agents")
async def list_agents():
    """List all available agents."""
    agents = []
    for name in agent_registry.list_agents():
        config = agent_registry.get_agent_config(name)
        agents.append({
            "name": name,
            "config": config,
        })
    return {"agents": agents}

# Agent interaction endpoint (non-streaming)
@router.post("/agent", response_model=AgentResponse)
async def agent_interaction(request: AgentRequest):
    """
    Interact with an agent without streaming.
    """
    # Get agent function
    agent_func = agent_registry.get_agent(request.agent)
    if not agent_func:
        raise HTTPException(status_code=404, detail=f"Agent '{request.agent}' not found")
    
    # Generate thread ID if not provided
    thread_id = request.thread_id or str(uuid.uuid4())
    
    # Prepare metadata
    metadata = request.metadata or {}
    metadata["thread_id"] = thread_id
    
    try:
        # Invoke agent
        result = await agent_func(
            message=request.message,
            metadata=metadata,
        )
        
        # Prepare response
        return AgentResponse(
            messages=result.get("messages", []),
            thread_id=thread_id,
            metadata=result.get("metadata"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Agent streaming endpoint
@router.post("/agent/stream")
async def agent_interaction_stream(request: AgentRequest):
    """
    Interact with an agent with streaming response.
    """
    # Get agent function
    agent_func = agent_registry.get_agent(request.agent)
    if not agent_func:
        raise HTTPException(status_code=404, detail=f"Agent '{request.agent}' not found")
    
    # Generate thread ID if not provided
    thread_id = request.thread_id or str(uuid.uuid4())
    
    # Prepare metadata
    metadata = request.metadata or {}
    metadata["thread_id"] = thread_id
    
    # Create streaming response
    return StreamingResponse(
        stream_agent_events(
            agent_func=agent_func,
            message=request.message,
            metadata=metadata,
        ),
        media_type="text/event-stream",
    )
```

### Agent Streaming
Create `app/streaming/agent_streaming.py`:

```python
# Example implementation
import json
import asyncio
from typing import Dict, Any, AsyncGenerator, Callable

async def stream_agent_events(
    agent_func: Callable,
    message: str,
    metadata: Dict[str, Any],
) -> AsyncGenerator[str, None]:
    """
    Stream events from an agent function.
    
    Args:
        agent_func: The agent function to call
        message: The user message
        metadata: Additional metadata for the agent
        
    Yields:
        SSE formatted event strings
    """
    # Configure the agent for streaming
    config = {"configurable": {"thread_id": metadata.get("thread_id")}}
    
    try:
        # Stream events from the agent
        async for event in agent_func.astream(
            message,
            metadata=metadata,
            config=config,
        ):
            # Format as SSE event
            if isinstance(event, dict):
                yield f"data: {json.dumps(event)}\n\n"
            else:
                # Handle other event types if needed
                yield f"data: {json.dumps({'type': 'event', 'content': str(event)})}\n\n"
    except Exception as e:
        # Send error event
        yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
    finally:
        # Send end event
        yield f"data: {json.dumps({'type': 'end'})}\n\n"
```

## Success Criteria
- FastAPI application correctly routes requests to agents
- Streaming works with SSE for real-time agent responses
- Error handling gracefully manages exceptions
- Health check endpoint provides system status
- API documentation is automatically generated by FastAPI
- Request validation prevents invalid inputs