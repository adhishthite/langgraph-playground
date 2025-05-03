"""Tests for the app configuration settings."""

import os
import pytest
from unittest.mock import patch

# Import the Settings class directly for testing
from app.config.settings import Settings


def test_settings_initialization(mock_env_vars):
    """Test that settings are properly initialized from environment variables."""
    test_settings = Settings()

    # Test Azure OpenAI settings
    assert test_settings.azure_openai.api_key == "test-api-key"
    assert (
        test_settings.azure_openai.endpoint == "https://test-endpoint.openai.azure.com"
    )
    assert test_settings.azure_openai.api_version == "2024-02-15-preview"

    # Test LangSmith settings
    assert test_settings.langsmith.api_key == "test-langsmith-key"
    assert test_settings.langsmith.tracing_enabled is True

    # Test Elasticsearch settings
    assert test_settings.elasticsearch.host == "localhost"
    assert test_settings.elasticsearch.port == 9200
    assert test_settings.elasticsearch.index_names == ["test-index-1", "test-index-2"]

    # Test Service settings
    assert test_settings.service.log_level.value == "DEBUG"
    assert test_settings.service.default_agent == "test-agent"
    assert test_settings.service.max_document_count == 10
    assert test_settings.service.rrf_k_factor == 50.0


def test_validate_required_settings(mock_env_vars):
    """Test validation of required environment variables."""
    test_settings = Settings()
    # This should not raise an exception
    assert test_settings.validate_required_settings() is True


def test_validate_missing_settings():
    """Test validation with missing required environment variables."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(Exception) as excinfo:
            # Create a new Settings instance with empty environment
            settings = Settings()
            settings.validate_required_settings()
        # Just assert that we got an error related to validation
        assert "validation error" in str(excinfo.value).lower()


def test_elasticsearch_index_parsing(mock_env_vars):
    """Test parsing of comma-separated Elasticsearch index names."""
    settings = Settings()
    assert len(settings.elasticsearch.index_names) == 2
    assert "test-index-1" in settings.elasticsearch.index_names
    assert "test-index-2" in settings.elasticsearch.index_names
