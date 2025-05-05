"""Isolated tests for Azure OpenAI client integration."""

import unittest
from unittest.mock import patch, MagicMock

import pytest


class TestAzureOpenAIClients(unittest.TestCase):
    """Test the Azure OpenAI client integration."""

    def setUp(self):
        """Set up test environment by patching settings."""
        self.settings_patcher = patch("app.config.settings.settings")
        self.mock_settings = self.settings_patcher.start()

        # Configure mock settings
        self.mock_settings.AZURE_OPENAI_API_KEY = "test-key"
        self.mock_settings.AZURE_OPENAI_ENDPOINT = (
            "https://test-endpoint.openai.azure.com"
        )
        self.mock_settings.AZURE_OPENAI_API_VERSION = "2023-05-15"
        self.mock_settings.AZURE_OPENAI_GPT4O_DEPLOYMENT = "test-deployment"
        self.mock_settings.AZURE_OPENAI_GPT4O_MINI_DEPLOYMENT = "test-mini-deployment"
        self.mock_settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT = (
            "test-embedding-deployment"
        )
        self.mock_settings.OPENAI_API_KEY = None
        self.mock_settings.OPENAI_API_BASE = None

    def tearDown(self):
        """Clean up patches."""
        self.settings_patcher.stop()

    @patch("app.core.llm_clients.AzureChatOpenAI")
    def test_get_azure_chat_model(self, mock_azure_chat):
        """Test creating an Azure chat model client."""
        from app.core.llm_clients import get_azure_chat_model

        mock_instance = MagicMock()
        mock_azure_chat.return_value = mock_instance

        result = get_azure_chat_model("test-deployment")

        self.assertEqual(result, mock_instance)
        mock_azure_chat.assert_called_once()

        # Check that the deployment name was passed correctly
        args, kwargs = mock_azure_chat.call_args
        self.assertEqual(kwargs["azure_deployment"], "test-deployment")
        self.assertIn("temperature", kwargs)
        self.assertIn("streaming", kwargs)

    @patch("app.core.llm_clients.AzureOpenAIEmbeddings")
    def test_get_embedding_model(self, mock_embeddings):
        """Test creating an Azure embeddings client."""
        from app.core.llm_clients import get_embedding_model

        mock_instance = MagicMock()
        mock_embeddings.return_value = mock_instance

        result = get_embedding_model()

        self.assertEqual(result, mock_instance)
        mock_embeddings.assert_called_once()

        # Check that the deployment name was passed correctly
        args, kwargs = mock_embeddings.call_args
        self.assertEqual(kwargs["azure_deployment"], "test-embedding-deployment")

    def test_get_embedding_model_no_deployment(self):
        """Test error when embedding deployment is not configured."""
        from app.core.llm_clients import get_embedding_model

        # Configure no deployment
        self.mock_settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT = None

        with self.assertRaises(ValueError):
            get_embedding_model()

    @patch("app.core.llm_clients.AzureChatOpenAI")
    def test_get_model_azure(self, mock_azure_chat):
        """Test getting a model by name with Azure."""
        from app.core.llm_clients import get_model

        mock_instance = MagicMock()
        mock_azure_chat.return_value = mock_instance

        # Test with valid model name
        result = get_model("gpt-4o")
        self.assertEqual(result, mock_instance)

        # Test with another valid model name
        result = get_model("gpt-4o-mini")
        self.assertEqual(result, mock_instance)

        # Test with invalid model name
        with self.assertRaises(ValueError):
            get_model("invalid-model")

    @patch("app.core.llm_clients.ChatOpenAI")
    def test_get_model_standard_openai(self, mock_chat_openai):
        """Test getting a model by name with standard OpenAI."""
        from app.core.llm_clients import get_model

        # Configure settings to use standard OpenAI
        self.mock_settings.AZURE_OPENAI_ENDPOINT = None
        self.mock_settings.AZURE_OPENAI_API_KEY = None
        self.mock_settings.OPENAI_API_KEY = "test-key"

        mock_instance = MagicMock()
        mock_chat_openai.return_value = mock_instance

        result = get_model("gpt-4")

        self.assertEqual(result, mock_instance)
        mock_chat_openai.assert_called_once()

        # Check that the model name was passed correctly
        args, kwargs = mock_chat_openai.call_args
        self.assertEqual(kwargs["model_name"], "gpt-4")

    def test_get_model_no_credentials(self):
        """Test error when no OpenAI credentials are configured."""
        from app.core.llm_clients import get_model

        # Configure settings with no credentials
        self.mock_settings.AZURE_OPENAI_ENDPOINT = None
        self.mock_settings.AZURE_OPENAI_API_KEY = None
        self.mock_settings.OPENAI_API_KEY = None

        with self.assertRaises(ValueError):
            get_model("gpt-4")

    def test_handle_api_error_decorator(self):
        """Test the API error handling decorator."""
        from openai import RateLimitError, APIError
        from app.core.llm_clients import handle_api_error, OpenAIClientError

        # Test function that will be decorated
        @handle_api_error
        def test_func(error_type=None):
            if error_type == "rate_limit":
                raise RateLimitError("Rate limit exceeded")
            elif error_type == "api_error":
                raise APIError("API error")
            elif error_type == "other":
                raise Exception("Other error")
            return "success"

        # Test success case
        self.assertEqual(test_func(), "success")

        # Test rate limit error
        with self.assertRaises(OpenAIClientError) as exc_info:
            test_func("rate_limit")
        self.assertIn("Rate limit exceeded", str(exc_info.exception))

        # Test API error
        with self.assertRaises(OpenAIClientError) as exc_info:
            test_func("api_error")
        self.assertIn("API error", str(exc_info.exception))

        # Test other error
        with self.assertRaises(OpenAIClientError) as exc_info:
            test_func("other")
        self.assertIn("Unexpected error", str(exc_info.exception))


if __name__ == "__main__":
    unittest.main()
