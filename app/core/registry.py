"""Agent registry for centralized management."""

from typing import Dict, Callable

from langgraph.graph import Graph


class AgentRegistry:
    """Registry for LangGraph agents."""

    def __init__(self):
        """Initialize an empty registry."""
        self._agents: Dict[str, Callable[..., Graph]] = {}

    def register(self, name: str, agent_factory: Callable[..., Graph]):
        """Register a new agent factory.

        Args:
            name: Name of the agent
            agent_factory: Function that creates a LangGraph agent
        """
        self._agents[name] = agent_factory

    def get(self, name: str):
        """Get an agent factory by name.

        Args:
            name: Name of the agent to retrieve

        Returns:
            The agent factory function
        """
        if name not in self._agents:
            raise KeyError(f"Agent '{name}' not found in registry")
        return self._agents[name]

    def list_agents(self):
        """List all registered agents.

        Returns:
            List of agent names
        """
        return list(self._agents.keys())


# Create a global registry instance
registry = AgentRegistry()
