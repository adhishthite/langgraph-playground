# 009-TASK: Testing Infrastructure

## Overview
Set up a comprehensive testing infrastructure using pytest for the LangGraph playground to ensure functionality, reliability, and maintainability.

## Requirements
- Create pytest configuration and fixtures
- Implement unit tests for key components
- Set up integration tests for the API
- Create fixtures for mocking external services
- Implement test coverage reporting

## Implementation Details

### Pytest Configuration
Create `tests/conftest.py` with fixtures and pytest configuration:

```python
# Example implementation
import pytest
import os
import asyncio
from typing import Dict, Any, Generator, AsyncGenerator
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app
from app.config.settings import Settings

# Test environment setup
@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Provide test settings with mock values."""
    return Settings(
        ENV_MODE="test",
        AZURE_OPENAI_API_KEY="test-key",
        AZURE_OPENAI_ENDPOINT="https://test-endpoint.openai.azure.com/",
        AZURE_OPENAI_API_VERSION="2023-05-15",
        AZURE_OPENAI_GPT4O_DEPLOYMENT="test-gpt4o",
        LANGCHAIN_API_KEY="test-langchain-key",
        API_DEBUG=True,
    )

# FastAPI test client
@pytest.fixture
def api_client(test_settings) -> Generator[TestClient, None, None]:
    """Create a FastAPI test client."""
    # Apply test settings
    with patch("app.config.settings.settings", test_settings):
        # Create test client
        with TestClient(app) as client:
            yield client

# Mock LLM client
@pytest.fixture
def mock_llm() -> MagicMock:
    """Mock LLM client for testing."""
    mock = MagicMock()
    mock.invoke.return_value = MagicMock(
        content="This is a test response",
        tool_calls=None,
    )
    mock.ainvoke = asyncio.coroutine(lambda *args, **kwargs: mock.invoke(*args, **kwargs))
    return mock

# Mock tools
@pytest.fixture
def mock_tools() -> Dict[str, MagicMock]:
    """Mock tools for testing."""
    tools = {}
    
    # Create mock date tool
    date_tool = MagicMock()
    date_tool.invoke.return_value = {
        "iso_format": "2023-05-01T12:00:00+00:00",
        "date": "2023-05-01",
        "time": "12:00:00",
        "day_of_week": "Monday",
        "timezone": "UTC",
    }
    date_tool.ainvoke = asyncio.coroutine(lambda *args, **kwargs: date_tool.invoke(*args, **kwargs))
    tools["get_current_date"] = date_tool
    
    # Create mock web scraper tool
    scraper_tool = MagicMock()
    scraper_tool.invoke.return_value = {
        "title": "Test Page",
        "content": "This is test content from a web page.",
        "url": "https://example.com",
        "metadata": {},
    }
    scraper_tool.ainvoke = asyncio.coroutine(lambda *args, **kwargs: scraper_tool.invoke(*args, **kwargs))
    tools["scrape_webpage"] = scraper_tool
    
    return tools

# Mock agent
@pytest.fixture
def mock_agent() -> MagicMock:
    """Mock agent for testing."""
    mock = MagicMock()
    mock.return_value = {
        "messages": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there! How can I help you today?"},
        ],
        "metadata": {"thread_id": "test-thread"},
    }
    mock.__call__ = asyncio.coroutine(lambda *args, **kwargs: mock.return_value)
    return mock
```

### Unit Tests
Create unit tests for key components, starting with tools:

```python
# tests/test_tools.py
import pytest
import json
from app.tools.date_tool import get_current_date, calculate_date_difference

def test_get_current_date():
    """Test the date tool returns correct structure."""
    result = get_current_date()
    
    assert isinstance(result, dict)
    assert "iso_format" in result
    assert "date" in result
    assert "time" in result
    assert "day_of_week" in result
    assert "timezone" in result
    assert result["timezone"] == "UTC"

def test_calculate_date_difference():
    """Test date difference calculation."""
    result = calculate_date_difference(
        start_date="2023-01-01",
        end_date="2023-01-10"
    )
    
    assert isinstance(result, dict)
    assert result["days"] == 9
    assert result["is_future"] == True
    assert result["is_past"] == False
```

Test the agent functionality:

```python
# tests/test_agents.py
import pytest
import asyncio
from unittest.mock import patch, MagicMock

from app.agents.openai_agents import react_agent

@pytest.mark.asyncio
async def test_react_agent_basic_response(mock_llm):
    """Test basic agent response without tools."""
    with patch("app.agents.openai_agents.get_model", return_value=mock_llm):
        result = await react_agent("Hello")
        
        assert "messages" in result
        assert len(result["messages"]) >= 1
        assert "metadata" in result

@pytest.mark.asyncio
async def test_react_agent_with_tools(mock_llm, mock_tools):
    """Test agent with tool execution."""
    # Configure mock to return tool calls
    mock_llm.invoke.return_value = MagicMock(
        content="I'll check the current date",
        tool_calls=[
            {
                "id": "tool-1",
                "name": "get_current_date",
                "arguments": {"timezone": "UTC"},
            }
        ],
    )
    
    with patch("app.agents.openai_agents.get_model", return_value=mock_llm), \
         patch("app.agents.openai_agents.get_tools", return_value=list(mock_tools.values())):
        result = await react_agent("What's the current date?")
        
        assert "messages" in result
        assert len(result["messages"]) >= 3  # User, LLM response, tool result
```

Test the API endpoints:

```python
# tests/test_api.py
import pytest
import json
from unittest.mock import patch

def test_health_check(api_client):
    """Test the health check endpoint."""
    response = api_client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_list_agents(api_client):
    """Test listing available agents."""
    response = api_client.get("/api/agents")
    assert response.status_code == 200
    assert "agents" in response.json()
    assert isinstance(response.json()["agents"], list)

@pytest.mark.asyncio
async def test_agent_interaction(api_client, mock_agent):
    """Test agent interaction endpoint."""
    with patch("app.api.routes.agent_registry.get_agent", return_value=mock_agent):
        response = api_client.post(
            "/api/agent",
            json={
                "message": "Hello",
                "agent": "react",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert "thread_id" in data
```

### Coverage Configuration
Create `.coveragerc` for coverage settings:

```ini
[run]
source = app
omit =
    */tests/*
    app/main.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
    if __name__ == "__main__":
    pass
    raise ImportError

[html]
directory = coverage_html
```

## Success Criteria
- Test configuration is properly set up with fixtures
- Unit tests cover key functionality of tools and agents
- API tests verify endpoint functionality
- Mocks replace external dependencies for isolated testing
- Coverage reporting identifies untested code
- Tests pass reliably and consistently