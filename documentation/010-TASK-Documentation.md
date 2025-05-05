# 010-TASK: Documentation and Examples

## Overview
Create comprehensive documentation and examples for using the LangGraph playground, including API usage, agent capabilities, and local development setup.

## Requirements
- Update the README with clear setup instructions
- Document available endpoints and their usage
- Create examples of using the API
- Document agent capabilities and parameters
- Include environment setup guidance
- Add code examples demonstrating key functionality

## Implementation Details

### README Update
Create a comprehensive project README with the following sections:

```markdown
# LangGraph Playground

A playground for experimenting with LangGraph ReAct agents, exposed via FastAPI.

## Features

- 🤖 LangGraph ReAct agents with functional API
- 🔧 Extensible tool framework including date/time and web scraping
- 🌐 FastAPI endpoints with streaming support
- 📝 Memory persistence for conversational context
- 📊 LangSmith integration for observability
- 🧪 Comprehensive testing infrastructure

## Quick Start

### Prerequisites

- Python 3.13+
- Azure OpenAI API access

### Installation

1. Clone this repository
   ```bash
   git clone https://github.com/yourusername/lg-playground.git
   cd lg-playground
   ```

2. Create and activate a virtual environment (optional but recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   uv run pip install -e .
   ```

4. Create a `.env` file with your configuration (see `.env.example` for required variables)

5. Start the API server
   ```bash
   uv run python -m app.main
   ```

6. Open http://localhost:8000/docs in your browser to see the API documentation

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| AZURE_OPENAI_API_KEY | Azure OpenAI API key | Yes | - |
| AZURE_OPENAI_ENDPOINT | Azure OpenAI endpoint URL | Yes | - |
| AZURE_OPENAI_API_VERSION | Azure OpenAI API version | No | 2023-05-15 |
| AZURE_OPENAI_GPT4O_DEPLOYMENT | Azure OpenAI GPT-4o deployment name | Yes | - |
| AZURE_OPENAI_GPT4O_MINI_DEPLOYMENT | Azure OpenAI GPT-4o-mini deployment name | No | - |
| LANGCHAIN_API_KEY | LangSmith API key for tracing | No | - |
| LANGCHAIN_PROJECT | LangSmith project name | No | lg-playground |
| ENV_MODE | Environment mode (development, test, production) | No | development |
| API_DEBUG | Enable debug mode for the API | No | False |

## API Usage

### Agent Interaction

```bash
# Basic interaction (non-streaming)
curl -X POST "http://localhost:8000/api/agent" \
  -H "Content-Type: application/json" \
  -d '{"message": "What time is it in Tokyo?", "agent": "react"}'

# Streaming interaction
curl -X POST "http://localhost:8000/api/agent/stream" \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about the latest news", "agent": "react"}'
```

### Available Agents

Use the `/api/agents` endpoint to get a list of available agents:

```bash
curl "http://localhost:8000/api/agents"
```

## Development

### Running Tests

```bash
uv run pip install -e ".[test]"
uv run pytest tests/
```

### Code Formatting and Linting

```bash
uv run pip install -e ".[lint]"
uv run black .
uv run ruff check .
```

## Project Structure

```
lg-playground/
├── app/
│   ├── api/            # API routes
│   ├── agents/         # Agent implementations
│   ├── config/         # Settings and configuration
│   ├── core/           # Core functionality
│   ├── streaming/      # Streaming support
│   ├── tools/          # Tool implementations
│   └── main.py         # FastAPI application
├── tests/              # Tests
├── .env.example        # Example environment variables
└── README.md           # This file
```
```

### API Documentation
Create a detailed API documentation file:

```markdown
# API Documentation

## Endpoints

### GET /api/health

Health check endpoint to verify the API is running.

**Response:**
```json
{
  "status": "ok"
}
```

### GET /api/agents

List all available agent implementations.

**Response:**
```json
{
  "agents": [
    {
      "name": "react",
      "config": {
        "description": "ReAct agent capable of using tools",
        "model": "gpt-4o",
        "supports_streaming": true,
        "supports_tools": true
      }
    }
  ]
}
```

### POST /api/agent

Interact with an agent (non-streaming).

**Request:**
```json
{
  "message": "What's the current time in Tokyo?",
  "agent": "react",
  "thread_id": "optional-thread-id",
  "metadata": {
    "system_prompt": "Optional custom system prompt"
  }
}
```

**Response:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "What's the current time in Tokyo?"
    },
    {
      "role": "assistant",
      "content": "I'll check the current time in Tokyo for you."
    },
    {
      "role": "function",
      "name": "get_current_date",
      "content": "{'iso_format': '2023-05-01T20:00:00+09:00', 'timezone': 'Asia/Tokyo', ...}"
    },
    {
      "role": "assistant",
      "content": "The current time in Tokyo is 8:00 PM on Monday, May 1st, 2023."
    }
  ],
  "thread_id": "conversation-thread-id",
  "metadata": {
    "system_prompt": "Custom system prompt if provided"
  }
}
```

### POST /api/agent/stream

Interact with an agent with streaming response.

**Request:**
Same as the non-streaming endpoint.

**Response:**
Server-sent events (SSE) stream with the following event formats:

```
data: {"type": "message", "content": {"role": "assistant", "content": "I'll check"}}

data: {"type": "message", "content": {"role": "assistant", "content": " the current time"}}

data: {"type": "function_call", "content": {"name": "get_current_date", "arguments": {"timezone": "Asia/Tokyo"}}}

data: {"type": "function_result", "content": {"iso_format": "2023-05-01T20:00:00+09:00", ...}}

data: {"type": "message", "content": {"role": "assistant", "content": "The current time in Tokyo is 8:00 PM."}}

data: {"type": "end"}
```
```

### Example Notebook
Create a Jupyter notebook demonstrating the API usage:

```python
# api_examples.ipynb

# API Usage Examples
import requests
import sseclient
import json

# Base URL for the API
BASE_URL = "http://localhost:8000/api"

# Check if the API is running
def check_health():
    response = requests.get(f"{BASE_URL}/health")
    print(f"API Health: {response.json()}")

# List available agents
def list_agents():
    response = requests.get(f"{BASE_URL}/agents")
    agents = response.json()["agents"]
    print(f"Available agents: {[a['name'] for a in agents]}")
    return agents

# Basic agent interaction
def agent_interaction(message, agent_name="react", thread_id=None):
    payload = {
        "message": message,
        "agent": agent_name,
    }
    
    if thread_id:
        payload["thread_id"] = thread_id
        
    response = requests.post(f"{BASE_URL}/agent", json=payload)
    return response.json()

# Streaming agent interaction
def agent_interaction_stream(message, agent_name="react", thread_id=None):
    payload = {
        "message": message,
        "agent": agent_name,
    }
    
    if thread_id:
        payload["thread_id"] = thread_id
        
    response = requests.post(f"{BASE_URL}/agent/stream", json=payload, stream=True)
    client = sseclient.SSEClient(response)
    
    full_response = []
    for event in client.events():
        data = json.loads(event.data)
        full_response.append(data)
        
        if data.get("type") == "message" and data.get("content", {}).get("role") == "assistant":
            print(f"Assistant: {data['content']['content']}")
        elif data.get("type") == "function_call":
            print(f"Tool Call: {data['content']['name']}")
        elif data.get("type") == "end":
            print("--- End of conversation ---")
            
    return full_response

# Examples

# Check API health
check_health()

# List available agents
agents = list_agents()

# Basic interaction
response = agent_interaction("What's the weather like in New York?")
print("\nBasic interaction:")
for message in response["messages"]:
    if message.get("role") == "user":
        print(f"User: {message['content']}")
    elif message.get("role") == "assistant":
        print(f"Assistant: {message['content']}")
        
# Save the thread ID for continuation
thread_id = response["thread_id"]
print(f"Thread ID: {thread_id}")

# Continue conversation
response = agent_interaction("What about London?", thread_id=thread_id)
print("\nContinuation:")
for message in response["messages"][-2:]:  # Only show the latest exchange
    if message.get("role") == "user":
        print(f"User: {message['content']}")
    elif message.get("role") == "assistant":
        print(f"Assistant: {message['content']}")

# Streaming example
print("\nStreaming example:")
full_response = agent_interaction_stream("Tell me a short joke")
```

## Success Criteria
- README provides clear setup instructions
- API documentation covers all endpoints and their usage
- Examples demonstrate key functionality
- Environment variables are well documented
- Project structure is clearly explained
- Documentation is accessible and easy to understand