"""Tests for Azure OpenAI client integration."""

import os
import unittest
from unittest.mock import patch, MagicMock

import pytest
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

# Apply patch to settings before importing the module
with patch("app.config.settings.settings") as mock_settings:
    # Set up mock settings
    mock_settings.AZURE_OPENAI_API_KEY = "test-key"
    mock_settings.AZURE_OPENAI_ENDPOINT = "https://test-endpoint.openai.azure.com"
    mock_settings.AZURE_OPENAI_API_VERSION = "2023-05-15"
    mock_settings.AZURE_OPENAI_GPT4O_DEPLOYMENT = "test-deployment"
    mock_settings.AZURE_OPENAI_GPT4O_MINI_DEPLOYMENT = "test-mini-deployment"
    mock_settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT = "test-embedding-deployment"
    mock_settings.OPENAI_API_KEY = None
    mock_settings.OPENAI_API_BASE = None

    # Import the module after mocking settings
    from app.core.llm_clients import (
        get_azure_chat_model,
        get_embedding_model,
        get_model,
        OpenAIClientError,
        handle_api_error,
    )


class TestAzureOpenAIClients:
    """Test the Azure OpenAI client integration."""

    @patch("app.core.llm_clients.AzureChatOpenAI")
    def test_get_azure_chat_model(self, mock_azure_chat):
        """Test creating an Azure chat model client."""
        mock_instance = MagicMock()
        mock_azure_chat.return_value = mock_instance

        result = get_azure_chat_model("test-deployment")

        assert result == mock_instance
        mock_azure_chat.assert_called_once()

        # Check that the deployment name was passed correctly
        args, kwargs = mock_azure_chat.call_args
        assert kwargs["azure_deployment"] == "test-deployment"
        assert "temperature" in kwargs
        assert "streaming" in kwargs

    @patch("app.core.llm_clients.AzureOpenAIEmbeddings")
    @patch("app.core.llm_clients.settings")
    def test_get_embedding_model(self, mock_settings, mock_embeddings):
        """Test creating an Azure embeddings client."""
        mock_settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT = "embedding-deployment"
        mock_instance = MagicMock()
        mock_embeddings.return_value = mock_instance

        result = get_embedding_model()

        assert result == mock_instance
        mock_embeddings.assert_called_once()

        # Check that the deployment name was passed correctly
        args, kwargs = mock_embeddings.call_args
        assert kwargs["azure_deployment"] == "embedding-deployment"

    @patch("app.core.llm_clients.settings")
    def test_get_embedding_model_no_deployment(self, mock_settings):
        """Test error when embedding deployment is not configured."""
        mock_settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT = None

        with pytest.raises(ValueError):
            get_embedding_model()

    @patch("app.core.llm_clients.AzureChatOpenAI")
    @patch("app.core.llm_clients.settings")
    def test_get_model_azure(self, mock_settings, mock_azure_chat):
        """Test getting a model by name with Azure."""
        # Configure settings to use Azure
        mock_settings.AZURE_OPENAI_ENDPOINT = "https://example.com"
        mock_settings.AZURE_OPENAI_API_KEY = "test-key"
        mock_settings.AZURE_OPENAI_GPT4O_DEPLOYMENT = "gpt4o-deployment"
        mock_settings.AZURE_OPENAI_GPT4O_MINI_DEPLOYMENT = "gpt4o-mini-deployment"

        mock_instance = MagicMock()
        mock_azure_chat.return_value = mock_instance

        # Test with valid model name
        result = get_model("gpt-4o")
        assert result == mock_instance

        # Test with another valid model name
        result = get_model("gpt-4o-mini")
        assert result == mock_instance

        # Test with invalid model name
        with pytest.raises(ValueError):
            get_model("invalid-model")

    @patch("app.core.llm_clients.ChatOpenAI")
    @patch("app.core.llm_clients.settings")
    def test_get_model_standard_openai(self, mock_settings, mock_chat_openai):
        """Test getting a model by name with standard OpenAI."""
        # Configure settings to use standard OpenAI
        mock_settings.AZURE_OPENAI_ENDPOINT = None
        mock_settings.AZURE_OPENAI_API_KEY = None
        mock_settings.OPENAI_API_KEY = "test-key"

        mock_instance = MagicMock()
        mock_chat_openai.return_value = mock_instance

        result = get_model("gpt-4")

        assert result == mock_instance
        mock_chat_openai.assert_called_once()

        # Check that the model name was passed correctly
        args, kwargs = mock_chat_openai.call_args
        assert kwargs["model_name"] == "gpt-4"

    @patch("app.core.llm_clients.settings")
    def test_get_model_no_credentials(self, mock_settings):
        """Test error when no OpenAI credentials are configured."""
        # Configure settings with no credentials
        mock_settings.AZURE_OPENAI_ENDPOINT = None
        mock_settings.AZURE_OPENAI_API_KEY = None
        mock_settings.OPENAI_API_KEY = None

        with pytest.raises(ValueError):
            get_model("gpt-4")

    @pytest.mark.asyncio
    async def test_handle_api_error_decorator(self):
        """Test the API error handling decorator."""

        # Create mock error classes with missing parameters
        class MockRateLimitError(Exception):
            def __init__(self, message):
                self.message = message
                super().__init__(message)

        class MockAPIError(Exception):
            def __init__(self, message):
                self.message = message
                super().__init__(message)

        # Test function that will be decorated
        @handle_api_error
        async def test_func(error_type=None):
            if error_type == "rate_limit":
                raise MockRateLimitError("Rate limit exceeded")
            elif error_type == "api_error":
                raise MockAPIError("API error")
            elif error_type == "other":
                raise Exception("Other error")
            return "success"

        # Test success case
        result = await test_func()
        assert result == "success"

        # Test rate limit error
        with pytest.raises(OpenAIClientError) as exc_info:
            await test_func("rate_limit")
        assert "Rate limit exceeded" in str(exc_info.value)

        # Test API error
        with pytest.raises(OpenAIClientError) as exc_info:
            await test_func("api_error")
        assert "API error" in str(exc_info.value)

        # Test other error
        with pytest.raises(OpenAIClientError) as exc_info:
            await test_func("other")
        assert "Unexpected error" in str(exc_info.value)
