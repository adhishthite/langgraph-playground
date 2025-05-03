# Action Plan for LangGraph Playground

This document provides detailed technical guidance for developing the LangGraph Playground application code.

## Technical Architecture

The LangGraph Playground implements a modular architecture with the following components:

### Agent Framework Integration

- **FastAPI**
- **Use `uv` for dependency management exclusively**

- **LangGraph**

- **LangSmith Tracing**: Full observability infrastructure

- **Pytest**: Full test suite for the project

### Agent Implementations

- **OpenAI Agents** (`openai_agents.py`)

  - LangGraph reAct agent (functional API)
  - Direct Azure OpenAI model access
  - GPT-4o and GPT-4o-mini model support
  - GPT-4.1, GPT-4.1-mini, and GPT-4.1-nano model support
  - Tool augmentation
  - System prompt configuration

- **Agent Registry** (`registry.py`)
  - Centralized agent management
  - Dynamic agent selection by name for the API
  - Consistent agent configuration

### Asynchronous API Implementation

- **FastAPI Integration** (`routes.py`)
  - Unified endpoint for all agents
  - SSE streaming with standardized format
  - Request validation
  - Error handling
  - Health check endpoints
  - Performance monitoring with LangSmith

### Azure OpenAI Integration

- **Client Management** (`llm_clients.py`)
  - Azure OpenAI client configuration
  - Model deployment selection
  - API version management
  - Embedding model configuration

### Function Tools

- **Date Tool** (`date_tool.py`)

  - Current date/time information

- **Web Scraping Tool** (`webscraper_tool.py`)
  - Use BeautifulSoup to scrape the web
  - URL content extraction
  - HTML processing and cleaning
  - Metadata retrieval
  - Error handling

### Streaming Infrastructure

- **Agent Streaming** (`agent_streaming.py`)
  - FastAPI SSE streaming
  - SSE event formatting
  - Plain text mode

## Code Architecture Details

### Agent Initialization Flow

1. Environment variables loaded from `.env` via `settings.py`
2. Azure OpenAI client created in `llm_clients.py`
3. Client configured as default for Agents SDK
4. LangSmith tracing processor registered
5. Agent registry populated with agent implementations
6. FastAPI router configured with agent endpoints

### Observability with LangSmith

1. Trace context created for each API request
2. Function spans recorded for key operations
3. Document retrieval metrics captured
4. Token usage measured for API calls
5. Latency metrics recorded for all operations
6. Error information preserved with context
