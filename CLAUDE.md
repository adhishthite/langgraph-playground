# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build/Test Commands

- Install dependencies: `pip install -e .`
- Install dev dependencies: `pip install -e ".[lint]"`
- Run linting: `ruff check .`
- Format code: `black .`
- Run a Python script: `python hello.py`
- Run Chainlit server: `chainlit run hello.py`

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

## LangGraph Documentation URLs

### Tutorials

- https://langchain-ai.github.io/langgraph/tutorials/introduction/
- https://langchain-ai.github.io/langgraph/tutorials/langgraph-platform/local-server/
- https://langchain-ai.github.io/langgraph/tutorials/workflows/

### Concepts

- https://langchain-ai.github.io/langgraph/concepts/
- https://langchain-ai.github.io/langgraph/concepts/agentic_concepts/
- https://langchain-ai.github.io/langgraph/concepts/application_structure/
- https://langchain-ai.github.io/langgraph/concepts/assistants/
- https://langchain-ai.github.io/langgraph/concepts/auth/
- https://langchain-ai.github.io/langgraph/concepts/bring_your_own_cloud/
- https://langchain-ai.github.io/langgraph/concepts/deployment_options/
- https://langchain-ai.github.io/langgraph/concepts/double_texting/
- https://langchain-ai.github.io/langgraph/concepts/durable_execution/
- https://langchain-ai.github.io/langgraph/concepts/faq/
- https://langchain-ai.github.io/langgraph/concepts/functional_api/
- https://langchain-ai.github.io/langgraph/concepts/high_level/
- https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/
- https://langchain-ai.github.io/langgraph/concepts/langgraph_cli/
- https://langchain-ai.github.io/langgraph/concepts/langgraph_cloud/
- https://langchain-ai.github.io/langgraph/concepts/langgraph_platform/
- https://langchain-ai.github.io/langgraph/concepts/langgraph_server/
- https://langchain-ai.github.io/langgraph/concepts/langgraph_studio/
- https://langchain-ai.github.io/langgraph/concepts/low_level/
- https://langchain-ai.github.io/langgraph/concepts/memory/
- https://langchain-ai.github.io/langgraph/concepts/multi_agent/
- https://langchain-ai.github.io/langgraph/concepts/persistence/
- https://langchain-ai.github.io/langgraph/concepts/plans/
- https://langchain-ai.github.io/langgraph/concepts/platform_architecture/
- https://langchain-ai.github.io/langgraph/concepts/pregel/
- https://langchain-ai.github.io/langgraph/concepts/scalability_and_resilience/
- https://langchain-ai.github.io/langgraph/concepts/sdk/
- https://langchain-ai.github.io/langgraph/concepts/self_hosted/
- https://langchain-ai.github.io/langgraph/concepts/streaming/
- https://langchain-ai.github.io/langgraph/concepts/template_applications/
- https://langchain-ai.github.io/langgraph/concepts/time-travel/

### How-to Guides

- https://langchain-ai.github.io/langgraph/how-tos/
- https://langchain-ai.github.io/langgraph/how-tos/agent-handoffs/
- https://langchain-ai.github.io/langgraph/how-tos/async/
- https://langchain-ai.github.io/langgraph/how-tos/autogen-integration/
- https://langchain-ai.github.io/langgraph/how-tos/autogen-integration-functional/
- https://langchain-ai.github.io/langgraph/how-tos/branching/
- https://langchain-ai.github.io/langgraph/how-tos/command
- https://langchain-ai.github.io/langgraph/how-tos/configuration/
- https://langchain-ai.github.io/langgraph/how-tos/create-react-agent/
- https://langchain-ai.github.io/langgraph/how-tos/create-react-agent-hitl/
- https://langchain-ai.github.io/langgraph/how-tos/create-react-agent-memory/
- https://langchain-ai.github.io/langgraph/how-tos/create-react-agent-structured-output/
- https://langchain-ai.github.io/langgraph/how-tos/create-react-agent-system-prompt/
- https://langchain-ai.github.io/langgraph/how-tos/cross-thread-persistence
- https://langchain-ai.github.io/langgraph/how-tos/cross-thread-persistence-functional
- https://langchain-ai.github.io/langgraph/how-tos/deploy-self-hosted/
- https://langchain-ai.github.io/langgraph/how-tos/disable-streaming/
- https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/edit-graph-state/
- https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/review-tool-calls/
- https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/time-travel/
- https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/wait-user-input/
- https://langchain-ai.github.io/langgraph/how-tos/input_output_schema/
- https://langchain-ai.github.io/langgraph/how-tos/many-tools/
- https://langchain-ai.github.io/langgraph/how-tos/map-reduce/
- https://langchain-ai.github.io/langgraph/how-tos/memory/add-summary-conversation-history/
- https://langchain-ai.github.io/langgraph/how-tos/memory/delete-messages
- https://langchain-ai.github.io/langgraph/how-tos/memory/manage-conversation-history/
- https://langchain-ai.github.io/langgraph/how-tos/memory/semantic-search/
- https://langchain-ai.github.io/langgraph/how-tos/multi-agent-multi-turn-convo/
- https://langchain-ai.github.io/langgraph/how-tos/multi-agent-multi-turn-convo-functional/
- https://langchain-ai.github.io/langgraph/how-tos/multi-agent-network/
- https://langchain-ai.github.io/langgraph/how-tos/multi-agent-network-functional/
- https://langchain-ai.github.io/langgraph/how-tos/node-retries/
- https://langchain-ai.github.io/langgraph/how-tos/pass-config-to-tools/
- https://langchain-ai.github.io/langgraph/how-tos/pass_private_state/
- https://langchain-ai.github.io/langgraph/how-tos/persistence/
- https://langchain-ai.github.io/langgraph/how-tos/persistence-functional/
- https://langchain-ai.github.io/langgraph/how-tos/persistence_mongodb/
- https://langchain-ai.github.io/langgraph/how-tos/persistence_postgres/
- https://langchain-ai.github.io/langgraph/how-tos/persistence_redis/
- https://langchain-ai.github.io/langgraph/how-tos/react-agent-from-scratch/
- https://langchain-ai.github.io/langgraph/how-tos/react-agent-from-scratch-functional
- https://langchain-ai.github.io/langgraph/how-tos/react-agent-structured-output
- https://langchain-ai.github.io/langgraph/how-tos/recursion-limit/
- https://langchain-ai.github.io/langgraph/how-tos/review-tool-calls-functional/
- https://langchain-ai.github.io/langgraph/how-tos/run-id-langsmith/
- https://langchain-ai.github.io/langgraph/how-tos/sequence/
- https://langchain-ai.github.io/langgraph/how-tos/state-model
- https://langchain-ai.github.io/langgraph/how-tos/state-reducers/
- https://langchain-ai.github.io/langgraph/how-tos/streaming/
- https://langchain-ai.github.io/langgraph/how-tos/streaming-events-from-within-tools/
- https://langchain-ai.github.io/langgraph/how-tos/streaming-specific-nodes/
- https://langchain-ai.github.io/langgraph/how-tos/streaming-subgraphs/
- https://langchain-ai.github.io/langgraph/how-tos/streaming-tokens
- https://langchain-ai.github.io/langgraph/how-tos/subgraph/
- https://langchain-ai.github.io/langgraph/how-tos/subgraph-persistence/
- https://langchain-ai.github.io/langgraph/how-tos/subgraph-transform-state/
- https://langchain-ai.github.io/langgraph/how-tos/subgraphs-manage-state/
- https://langchain-ai.github.io/langgraph/how-tos/tool-calling/
- https://langchain-ai.github.io/langgraph/how-tos/tool-calling-errors/
- https://langchain-ai.github.io/langgraph/how-tos/update-state-from-tools/
- https://langchain-ai.github.io/langgraph/how-tos/use-remote-graph/
- https://langchain-ai.github.io/langgraph/how-tos/visualization
- https://langchain-ai.github.io/langgraph/how-tos/wait-user-input-functional/
