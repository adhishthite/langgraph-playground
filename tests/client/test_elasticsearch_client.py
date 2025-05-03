"""
Tests for the Elasticsearch client.

Tests the initialization and connection of the Elasticsearch client.
"""

import os
from unittest.mock import patch, MagicMock

import pytest

from app.client.elasticsearch_client import get_elasticsearch_client


@pytest.fixture
def mock_elasticsearch():
    """Mock the Elasticsearch client."""
    with patch("app.client.elasticsearch_client.Elasticsearch") as mock_es:
        mock_instance = MagicMock()
        mock_es.return_value = mock_instance
        yield mock_es, mock_instance


@pytest.fixture
def mock_es_settings():
    """Mock Elasticsearch settings."""
    with patch("app.client.elasticsearch_client.elasticsearch_settings") as mock_settings:
        mock_settings.host = "test-host"
        # port is now fixed at 9200 in the code
        mock_settings.user = None
        mock_settings.password = None
        mock_settings.index_names = ["test-index"]
        yield mock_settings


def test_get_elasticsearch_client_with_no_settings():
    """Test that the client returns None when settings are None."""
    with patch("app.client.elasticsearch_client.elasticsearch_settings", None):
        client = get_elasticsearch_client()
        assert client is None


def test_get_elasticsearch_client_with_basic_settings(mock_elasticsearch, mock_es_settings):
    """Test that the client is created with basic settings."""
    mock_es, mock_instance = mock_elasticsearch
    
    with patch.dict(os.environ, {}, clear=True):  # Ensure no ES_API_KEY in env
        client = get_elasticsearch_client()
        
        assert client == mock_instance
        mock_es.assert_called_once()
        # Check that it was called with the correct host
        assert mock_es.call_args.kwargs["hosts"] == ["test-host"]
        # Check basic auth wasn't used
        assert "basic_auth" not in mock_es.call_args.kwargs or mock_es.call_args.kwargs["basic_auth"] is None
        # Check api_key wasn't used
        assert "api_key" not in mock_es.call_args.kwargs or mock_es.call_args.kwargs["api_key"] is None


def test_get_elasticsearch_client_with_auth_settings(mock_elasticsearch, mock_es_settings):
    """Test that the client is created with authentication settings."""
    mock_es, mock_instance = mock_elasticsearch
    mock_es_settings.user = "user"
    mock_es_settings.password = "password"
    
    with patch.dict(os.environ, {}, clear=True):  # Ensure no ES_API_KEY in env
        client = get_elasticsearch_client()
        
        assert client == mock_instance
        mock_es.assert_called_once()
        # Check that basic auth was used with correct credentials
        assert mock_es.call_args.kwargs["basic_auth"] == ("user", "password")


def test_get_elasticsearch_client_with_api_key(mock_elasticsearch, mock_es_settings):
    """Test that the client is created with API key."""
    mock_es, mock_instance = mock_elasticsearch
    
    with patch.dict(os.environ, {"ES_API_KEY": "test-api-key"}, clear=True):
        client = get_elasticsearch_client()
        
        assert client == mock_instance
        mock_es.assert_called_once()
        # Check that API key was used
        assert mock_es.call_args.kwargs["api_key"] == "test-api-key"


def test_get_elasticsearch_client_with_auth_and_api_key(mock_elasticsearch, mock_es_settings):
    """Test that the client is created with both basic auth and API key."""
    mock_es, mock_instance = mock_elasticsearch
    mock_es_settings.user = "user"
    mock_es_settings.password = "password"
    
    with patch.dict(os.environ, {"ES_API_KEY": "test-api-key"}, clear=True):
        client = get_elasticsearch_client()
        
        assert client == mock_instance
        mock_es.assert_called_once()
        # Both auth methods should be present
        assert mock_es.call_args.kwargs["basic_auth"] == ("user", "password")
        assert mock_es.call_args.kwargs["api_key"] == "test-api-key"