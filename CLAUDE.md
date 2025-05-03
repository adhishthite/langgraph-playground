# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build/Test Commands

- Install dependencies: `uv run pip install -e .`
- Install dev dependencies: `uv run pip install -e ".[lint]"`
- Run linting: `uv run ruff check .`
- Format code: `uv run black .`
- Run a Python script: `uv run python hello.py`
- Run tests: `uv run pytest tests/`

## Project Guidelines

1. We will exclusively use LangGraph for development
2. We need a clear directory structure
3. Use `uv run` for all Python commands

## Code Style Guidelines

- **Imports**: Group standard library, third-party, and local imports separately
- **Formatting**: Follow Black formatting conventions
- **Types**: Use type hints for function parameters and return values
- **Documentation**:
  - Use docstrings for functions and classes
  - Follow Google-style docstring format with Args/Returns sections
- **Naming Conventions**:
  - snake_case for variables and functions
  - PascalCase for classes
  - Use descriptive names that reflect purpose
- **Error Handling**:
  - Use try/except blocks appropriately
  - Provide informative error messages
- **LangGraph Guidelines**:
  - Define tools with @tool decorator
  - Use @task for LangGraph tasks
  - Use @entrypoint for LangGraph entry points
  - Follow functional API patterns for complex workflows
- **Directory Structure**:
  - Use app/ folder for application code, settings and configuration
  - Use tests/ folder for Pytest test files
  - Organize code into logical modules

## LangGraph Documentation URLs

### Tutorials

- [Introduction](https://langchain-ai.github.io/langgraph/tutorials/introduction/)
- [Local Server](https://langchain-ai.github.io/langgraph/tutorials/langgraph-platform/local-server/)
- [Workflows](https://langchain-ai.github.io/langgraph/tutorials/workflows/)

### Concepts

- [Overview](https://langchain-ai.github.io/langgraph/concepts/)
- [Agentic Concepts](https://langchain-ai.github.io/langgraph/concepts/agentic_concepts/)
- [Application Structure](https://langchain-ai.github.io/langgraph/concepts/application_structure/)
- [Assistants](https://langchain-ai.github.io/langgraph/concepts/assistants/)
- [Authentication](https://langchain-ai.github.io/langgraph/concepts/auth/)
- [Bring Your Own Cloud](https://langchain-ai.github.io/langgraph/concepts/bring_your_own_cloud/)
- [Deployment Options](https://langchain-ai.github.io/langgraph/concepts/deployment_options/)
- [Double Texting](https://langchain-ai.github.io/langgraph/concepts/double_texting/)
- [Durable Execution](https://langchain-ai.github.io/langgraph/concepts/durable_execution/)
- [FAQ](https://langchain-ai.github.io/langgraph/concepts/faq/)
- [Functional API](https://langchain-ai.github.io/langgraph/concepts/functional_api/)
- [High Level](https://langchain-ai.github.io/langgraph/concepts/high_level/)
- [Human in the Loop](https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/)
- [LangGraph CLI](https://langchain-ai.github.io/langgraph/concepts/langgraph_cli/)
- [LangGraph Cloud](https://langchain-ai.github.io/langgraph/concepts/langgraph_cloud/)
- [LangGraph Platform](https://langchain-ai.github.io/langgraph/concepts/langgraph_platform/)
- [LangGraph Server](https://langchain-ai.github.io/langgraph/concepts/langgraph_server/)
- [LangGraph Studio](https://langchain-ai.github.io/langgraph/concepts/langgraph_studio/)
- [Low Level](https://langchain-ai.github.io/langgraph/concepts/low_level/)
- [Memory](https://langchain-ai.github.io/langgraph/concepts/memory/)
- [Multi Agent](https://langchain-ai.github.io/langgraph/concepts/multi_agent/)
- [Persistence](https://langchain-ai.github.io/langgraph/concepts/persistence/)
- [Plans](https://langchain-ai.github.io/langgraph/concepts/plans/)
- [Platform Architecture](https://langchain-ai.github.io/langgraph/concepts/platform_architecture/)
- [Pregel](https://langchain-ai.github.io/langgraph/concepts/pregel/)
- [Scalability and Resilience](https://langchain-ai.github.io/langgraph/concepts/scalability_and_resilience/)
- [SDK](https://langchain-ai.github.io/langgraph/concepts/sdk/)
- [Self Hosted](https://langchain-ai.github.io/langgraph/concepts/self_hosted/)
- [Streaming](https://langchain-ai.github.io/langgraph/concepts/streaming/)
- [Template Applications](https://langchain-ai.github.io/langgraph/concepts/template_applications/)
- [Time Travel](https://langchain-ai.github.io/langgraph/concepts/time-travel/)

### How-to Guides

- [Overview](https://langchain-ai.github.io/langgraph/how-tos/)
- [Agent Handoffs](https://langchain-ai.github.io/langgraph/how-tos/agent-handoffs/)
- [Async](https://langchain-ai.github.io/langgraph/how-tos/async/)
- [AutoGen Integration](https://langchain-ai.github.io/langgraph/how-tos/autogen-integration/)
- [AutoGen Integration Functional](https://langchain-ai.github.io/langgraph/how-tos/autogen-integration-functional/)
- [Branching](https://langchain-ai.github.io/langgraph/how-tos/branching/)
- [Command](https://langchain-ai.github.io/langgraph/how-tos/command)
- [Configuration](https://langchain-ai.github.io/langgraph/how-tos/configuration/)
- [Create React Agent](https://langchain-ai.github.io/langgraph/how-tos/create-react-agent/)
- [Create React Agent HITL](https://langchain-ai.github.io/langgraph/how-tos/create-react-agent-hitl/)
- [Create React Agent Memory](https://langchain-ai.github.io/langgraph/how-tos/create-react-agent-memory/)
- [Create React Agent Structured Output](https://langchain-ai.github.io/langgraph/how-tos/create-react-agent-structured-output/)
- [Create React Agent System Prompt](https://langchain-ai.github.io/langgraph/how-tos/create-react-agent-system-prompt/)
- [Cross Thread Persistence](https://langchain-ai.github.io/langgraph/how-tos/cross-thread-persistence)
- [Cross Thread Persistence Functional](https://langchain-ai.github.io/langgraph/how-tos/cross-thread-persistence-functional)
- [Deploy Self Hosted](https://langchain-ai.github.io/langgraph/how-tos/deploy-self-hosted/)
- [Disable Streaming](https://langchain-ai.github.io/langgraph/how-tos/disable-streaming/)
- [Edit Graph State](https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/edit-graph-state/)
- [Review Tool Calls](https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/review-tool-calls/)
- [Time Travel](https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/time-travel/)
- [Wait User Input](https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/wait-user-input/)
- [Input Output Schema](https://langchain-ai.github.io/langgraph/how-tos/input_output_schema/)
- [Many Tools](https://langchain-ai.github.io/langgraph/how-tos/many-tools/)
- [Map Reduce](https://langchain-ai.github.io/langgraph/how-tos/map-reduce/)
- [Add Summary Conversation History](https://langchain-ai.github.io/langgraph/how-tos/memory/add-summary-conversation-history/)
- [Delete Messages](https://langchain-ai.github.io/langgraph/how-tos/memory/delete-messages)
- [Manage Conversation History](https://langchain-ai.github.io/langgraph/how-tos/memory/manage-conversation-history/)
- [Semantic Search](https://langchain-ai.github.io/langgraph/how-tos/memory/semantic-search/)
- [Multi Agent Multi Turn Conversation](https://langchain-ai.github.io/langgraph/how-tos/multi-agent-multi-turn-convo/)
- [Multi Agent Multi Turn Conversation Functional](https://langchain-ai.github.io/langgraph/how-tos/multi-agent-multi-turn-convo-functional/)
- [Multi Agent Network](https://langchain-ai.github.io/langgraph/how-tos/multi-agent-network/)
- [Multi Agent Network Functional](https://langchain-ai.github.io/langgraph/how-tos/multi-agent-network-functional/)
- [Node Retries](https://langchain-ai.github.io/langgraph/how-tos/node-retries/)
- [Pass Config to Tools](https://langchain-ai.github.io/langgraph/how-tos/pass-config-to-tools/)
- [Pass Private State](https://langchain-ai.github.io/langgraph/how-tos/pass_private_state/)
- [Persistence](https://langchain-ai.github.io/langgraph/how-tos/persistence/)
- [Persistence Functional](https://langchain-ai.github.io/langgraph/how-tos/persistence-functional/)
- [Persistence MongoDB](https://langchain-ai.github.io/langgraph/how-tos/persistence_mongodb/)
- [Persistence Postgres](https://langchain-ai.github.io/langgraph/how-tos/persistence_postgres/)
- [Persistence Redis](https://langchain-ai.github.io/langgraph/how-tos/persistence_redis/)
- [React Agent From Scratch](https://langchain-ai.github.io/langgraph/how-tos/react-agent-from-scratch/)
- [React Agent From Scratch Functional](https://langchain-ai.github.io/langgraph/how-tos/react-agent-from-scratch-functional)
- [React Agent Structured Output](https://langchain-ai.github.io/langgraph/how-tos/react-agent-structured-output)
- [Recursion Limit](https://langchain-ai.github.io/langgraph/how-tos/recursion-limit/)
- [Review Tool Calls Functional](https://langchain-ai.github.io/langgraph/how-tos/review-tool-calls-functional/)
- [Run ID LangSmith](https://langchain-ai.github.io/langgraph/how-tos/run-id-langsmith/)
- [Sequence](https://langchain-ai.github.io/langgraph/how-tos/sequence/)
- [State Model](https://langchain-ai.github.io/langgraph/how-tos/state-model)
- [State Reducers](https://langchain-ai.github.io/langgraph/how-tos/state-reducers/)
- [Streaming](https://langchain-ai.github.io/langgraph/how-tos/streaming/)
- [Streaming Events From Within Tools](https://langchain-ai.github.io/langgraph/how-tos/streaming-events-from-within-tools/)
- [Streaming Specific Nodes](https://langchain-ai.github.io/langgraph/how-tos/streaming-specific-nodes/)
- [Streaming Subgraphs](https://langchain-ai.github.io/langgraph/how-tos/streaming-subgraphs/)
- [Streaming Tokens](https://langchain-ai.github.io/langgraph/how-tos/streaming-tokens)
- [Subgraph](https://langchain-ai.github.io/langgraph/how-tos/subgraph/)
- [Subgraph Persistence](https://langchain-ai.github.io/langgraph/how-tos/subgraph-persistence/)
- [Subgraph Transform State](https://langchain-ai.github.io/langgraph/how-tos/subgraph-transform-state/)
- [Subgraphs Manage State](https://langchain-ai.github.io/langgraph/how-tos/subgraphs-manage-state/)
- [Tool Calling](https://langchain-ai.github.io/langgraph/how-tos/tool-calling/)
- [Tool Calling Errors](https://langchain-ai.github.io/langgraph/how-tos/tool-calling-errors/)
- [Update State From Tools](https://langchain-ai.github.io/langgraph/how-tos/update-state-from-tools/)
- [Use Remote Graph](https://langchain-ai.github.io/langgraph/how-tos/use-remote-graph/)
- [Visualization](https://langchain-ai.github.io/langgraph/how-tos/visualization)
- [Wait User Input Functional](https://langchain-ai.github.io/langgraph/how-tos/wait-user-input-functional/)
