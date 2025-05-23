# LangGraph Playground

A playground environment for experimenting with [LangGraph](https://github.com/langchain-ai/langgraph) - a library for building stateful, multi-actor applications with LLMs.

## Features

- FastAPI integration
- OpenAI agent implementation
- Streaming support for agent interactions
- Tool integration (date/time and web scraper examples)
- WebSocket support for real-time communication

## Directory Structure

```
lg-playground/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py          # FastAPI routes
│   ├── agents/
│   │   ├── __init__.py
│   │   └── openai_agents.py   # OpenAI-based agents using LangGraph
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py        # Environment and application settings
│   ├── core/
│   │   ├── __init__.py
│   │   ├── llm_clients.py     # OpenAI client setup
│   │   └── registry.py        # Agent registry for centralized management
│   ├── streaming/
│   │   ├── __init__.py
│   │   └── agent_streaming.py # Streaming infrastructure
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── date_tool.py       # Date/time information tool
│   │   └── webscraper_tool.py # Web scraping tool
│   └── main.py                # FastAPI application entry point
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Pytest fixtures and configuration
│   ├── test_agents.py
│   ├── test_tools.py
│   └── test_api.py
└── README.md                  # Project documentation
```

## Setup Instructions

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd lg-playground
   ```

2. Set up a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   uv run pip install -e .
   ```

4. Install development dependencies:
   ```bash
   uv run pip install -e ".[lint]"
   ```

5. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## Usage

1. Run the FastAPI application:
   ```bash
   uv run python -m app.main
   ```

   The API will be available at http://localhost:8000

2. Use the WebSocket endpoint:
   ```
   ws://localhost:8000/ws/agent/{agent_name}
   ```

## Development

- Run linting:
  ```bash
  uv run ruff check .
  ```

- Format code:
  ```bash
  uv run black .
  ```

- Run tests:
  ```bash
  uv run pytest tests/
  ```

## Documentation

For more information about LangGraph, visit the official documentation:
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Documentation](https://python.langchain.com/docs/get_started)