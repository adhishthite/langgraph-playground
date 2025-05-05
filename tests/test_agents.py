"""Tests for agent functionality."""

import pytest
from unittest.mock import patch

from app.core.registry import registry, AgentRegistry


def test_agent_registry():
    """Test the agent registry."""
    # Create a test registry
    test_registry = AgentRegistry()

    # Register a mock agent
    def mock_agent_factory():
        return "mock_agent"

    test_registry.register("test_agent", mock_agent_factory)

    # Test retrieval
    assert test_registry.get("test_agent")() == "mock_agent"

    # Test listing
    assert "test_agent" in test_registry.list_agents()

    # Test KeyError for non-existent agent
    with pytest.raises(KeyError):
        test_registry.get("non_existent_agent")
