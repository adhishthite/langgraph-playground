# 008-TASK: LangSmith Integration

## Overview
Integrate LangSmith tracing into the application for observability of agent workflows, tool usage, and performance metrics.

## Requirements
- Set up LangSmith tracing for the entire application
- Configure trace context for each API request
- Record function spans for key operations
- Capture token usage and other metrics
- Enable trace visualization through LangSmith UI

## Implementation Details

### LangSmith Configuration
Update `app/config/settings.py` to include LangSmith settings:

```python
# Add to existing Settings class
LANGCHAIN_TRACING_V2: bool = True
LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"
LANGCHAIN_API_KEY: str
LANGCHAIN_PROJECT: str = "lg-playground"
```

### Tracing Integration
Create a utility module for tracing in `app/core/tracing.py`:

```python
# Example implementation
from typing import Optional, Dict, Any, Callable, TypeVar, ParamSpec, cast
import functools
import time
import os
import uuid
from langsmith import Client
from langsmith.run_trees import RunTree
from app.config.settings import settings

# Configure LangChain tracing
def configure_langsmith():
    """Configure LangSmith tracing environment variables."""
    os.environ["LANGCHAIN_TRACING_V2"] = str(settings.LANGCHAIN_TRACING_V2).lower()
    if settings.LANGCHAIN_API_KEY:
        os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
    os.environ["LANGCHAIN_ENDPOINT"] = settings.LANGCHAIN_ENDPOINT
    os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT

# Initialize LangSmith client
langsmith_client = Client(
    api_key=settings.LANGCHAIN_API_KEY,
    api_url=settings.LANGCHAIN_ENDPOINT,
)

# Create trace context
def create_trace_context(
    name: str,
    run_id: Optional[str] = None,
    tags: Optional[list] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> RunTree:
    """
    Create a trace context for tracking operations.
    
    Args:
        name: The name of the trace
        run_id: Optional run ID for the trace
        tags: Optional tags for the trace
        metadata: Optional metadata for the trace
        
    Returns:
        RunTree instance for the trace
    """
    run_id = run_id or str(uuid.uuid4())
    return RunTree(
        name=name,
        run_id=run_id,
        tags=tags or [],
        metadata=metadata or {},
    )

# Function decorator for tracing
P = ParamSpec("P")
T = TypeVar("T")

def traced(
    name: Optional[str] = None, 
    tags: Optional[list] = None,
    metadata_fn: Optional[Callable[..., Dict[str, Any]]] = None,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator to trace a function using LangSmith.
    
    Args:
        name: Name of the trace (defaults to function name)
        tags: Tags for the trace
        metadata_fn: Function to extract additional metadata from function args
        
    Returns:
        Decorated function with tracing
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Skip tracing if disabled
            if not settings.LANGCHAIN_TRACING_V2:
                return func(*args, **kwargs)
                
            # Get trace name
            trace_name = name or func.__name__
            
            # Get additional metadata
            metadata = {}
            if metadata_fn:
                metadata = metadata_fn(*args, **kwargs)
            
            # Start timing
            start_time = time.time()
            
            try:
                # Execute function within trace context
                with create_trace_context(
                    name=trace_name,
                    tags=tags,
                    metadata=metadata,
                ) as run:
                    result = func(*args, **kwargs)
                    
                    # Record duration
                    duration = time.time() - start_time
                    run.add_metadata({"duration_seconds": duration})
                    
                    return result
            except Exception as e:
                # Record error
                duration = time.time() - start_time
                with create_trace_context(
                    name=f"{trace_name}:error",
                    tags=tags + ["error"] if tags else ["error"],
                    metadata={
                        **metadata,
                        "duration_seconds": duration,
                        "error": str(e),
                        "error_type": type(e).__name__,
                    },
                ):
                    raise
        
        # Handle async functions
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                # Skip tracing if disabled
                if not settings.LANGCHAIN_TRACING_V2:
                    return await func(*args, **kwargs)
                
                # Get trace name
                trace_name = name or func.__name__
                
                # Get additional metadata
                metadata = {}
                if metadata_fn:
                    metadata = metadata_fn(*args, **kwargs)
                
                # Start timing
                start_time = time.time()
                
                try:
                    # Execute function within trace context
                    with create_trace_context(
                        name=trace_name,
                        tags=tags,
                        metadata=metadata,
                    ) as run:
                        result = await func(*args, **kwargs)
                        
                        # Record duration
                        duration = time.time() - start_time
                        run.add_metadata({"duration_seconds": duration})
                        
                        return result
                except Exception as e:
                    # Record error
                    duration = time.time() - start_time
                    with create_trace_context(
                        name=f"{trace_name}:error",
                        tags=tags + ["error"] if tags else ["error"],
                        metadata={
                            **metadata,
                            "duration_seconds": duration,
                            "error": str(e),
                            "error_type": type(e).__name__,
                        },
                    ):
                        raise
            
            return cast(Callable[P, T], async_wrapper)
        
        return cast(Callable[P, T], wrapper)
    
    return decorator
```

### Integration with FastAPI
Add middleware to the FastAPI application in `app/main.py`:

```python
from app.core.tracing import configure_langsmith

# Configure LangSmith at application startup
@app.on_event("startup")
async def startup_event():
    """Configure services on startup."""
    configure_langsmith()

# Add trace context to requests
@app.middleware("http")
async def add_trace_context(request: Request, call_next):
    """Add trace context to requests."""
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    
    with create_trace_context(
        name=f"http:{request.method}:{request.url.path}",
        run_id=request_id,
        tags=["http", request.method.lower()],
        metadata={
            "method": request.method,
            "path": request.url.path,
            "query": dict(request.query_params),
        },
    ):
        response = await call_next(request)
    
    return response
```

### Using Tracing in Agents
Apply the tracing decorator to key functions in agent implementations:

```python
from app.core.tracing import traced

@traced(name="react_agent", tags=["agent", "react"])
@entrypoint(checkpointer=MemorySaver())
async def react_agent(message: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """ReAct agent implementation with tracing."""
    # Implementation details...
```

## Success Criteria
- LangSmith tracing is properly configured with environment variables
- API requests are traced with relevant metadata
- Agent execution is tracked with detailed spans
- Tool usage and performance metrics are captured
- Errors are properly recorded with context
- Traces can be visualized in LangSmith UI