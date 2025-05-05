# 006-TASK: Agent Registry

## Overview
Create a centralized agent registry system that manages and provides access to different agent implementations throughout the application.

## Requirements
- Create a registry for managing all agent implementations
- Support dynamic agent selection by name
- Provide consistent agent configuration
- Allow for new agent types to be added easily
- Enable feature flags for different agent capabilities

## Implementation Details

### Registry Module
Create `app/core/registry.py` with the following features:

```python
# Example implementation
from typing import Dict, Any, Callable, Optional, List
from langchain_core.language_models import BaseChatModel

from app.agents.openai_agents import react_agent
from app.config.settings import settings

class AgentRegistry:
    """
    Registry for managing all agent implementations in the application.
    """
    
    def __init__(self):
        """Initialize the agent registry."""
        self._agents = {}
        self._configs = {}
        self._register_defaults()
    
    def _register_defaults(self):
        """Register default agent implementations."""
        # Register the ReAct agent
        self.register_agent(
            "react",
            react_agent,
            {
                "description": "ReAct agent capable of using tools",
                "model": "gpt-4o",
                "supports_streaming": True,
                "supports_tools": True,
            }
        )
        
        # Additional agents can be registered here
    
    def register_agent(
        self, 
        name: str, 
        agent_func: Callable, 
        config: Dict[str, Any]
    ) -> None:
        """
        Register an agent implementation in the registry.
        
        Args:
            name: The name of the agent
            agent_func: The agent function or class
            config: Configuration parameters for the agent
        """
        self._agents[name] = agent_func
        self._configs[name] = config
    
    def get_agent(self, name: str) -> Optional[Callable]:
        """
        Get an agent by name.
        
        Args:
            name: The name of the agent
        
        Returns:
            The agent function or None if not found
        """
        return self._agents.get(name)
    
    def get_agent_config(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get the configuration for an agent by name.
        
        Args:
            name: The name of the agent
            
        Returns:
            The agent configuration or None if not found
        """
        return self._configs.get(name)
    
    def list_agents(self) -> List[str]:
        """
        List all available agent names.
        
        Returns:
            List of agent names
        """
        return list(self._agents.keys())
    
    def agent_exists(self, name: str) -> bool:
        """
        Check if an agent exists in the registry.
        
        Args:
            name: The name of the agent
            
        Returns:
            True if the agent exists, False otherwise
        """
        return name in self._agents

# Create a global instance of the registry
agent_registry = AgentRegistry()

# Helper function to get default agent
def get_default_agent():
    """
    Get the default agent implementation.
    
    Returns:
        The default agent function
    """
    return agent_registry.get_agent(settings.DEFAULT_AGENT or "react")
```

### Integration with API
- Ensure the registry is accessible from API routes
- Use registry to validate agent names in requests
- Allow API to specify which agent to use for a given request

## Success Criteria
- Agent registry provides a central point for accessing agent implementations
- New agent types can be added without changing other code
- Agent configuration is consistent and easily accessible
- The API can use the registry to route requests to the appropriate agent
- Default agent selection works correctly