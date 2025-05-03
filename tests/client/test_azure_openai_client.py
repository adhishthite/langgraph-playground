"""
Tests for the Azure OpenAI client module.
"""

import unittest
from unittest.mock import patch, MagicMock

from app.client.azure_openai_client import (
    get_azure_openai_client,
    get_azure_openai_completion,
    get_azure_openai_embedding,
    get_available_models,
    AzureOpenAIClientPool,
    ModelNotAvailableError,
)


class TestAzureOpenAIClient(unittest.TestCase):
    """Test the Azure OpenAI client functions."""

    @patch("app.client.azure_openai_client.azure_openai_settings")
    @patch("app.client.azure_openai_client.AzureOpenAI")
    def test_get_azure_openai_client(self, mock_azure_openai, mock_settings):
        """Test client initialization."""
        # Setup
        mock_settings.api_key = "test-api-key"
        mock_settings.endpoint = "https://test-endpoint.openai.azure.com"
        mock_settings.api_version = "2024-02-15-preview"

        # Execute
        client = get_azure_openai_client()

        # Verify
        mock_azure_openai.assert_called_once_with(
            api_key="test-api-key",
            azure_endpoint="https://test-endpoint.openai.azure.com",
            api_version="2024-02-15-preview",
        )
        self.assertEqual(client, mock_azure_openai.return_value)

    @patch("app.client.azure_openai_client.azure_openai_settings")
    def test_get_azure_openai_client_missing_settings(self, mock_settings):
        """Test client initialization with missing settings."""
        # Setup
        mock_settings.api_key = ""
        mock_settings.endpoint = "https://test-endpoint.openai.azure.com"

        # Execute
        client = get_azure_openai_client()

        # Verify
        self.assertIsNone(client)

    def test_get_azure_openai_client_no_settings(self):
        """Test client initialization with no settings."""
        # Setup - patch the module directly
        with patch("app.client.azure_openai_client.azure_openai_settings", None):
            # Execute
            client = get_azure_openai_client()

            # Verify
            self.assertIsNone(client)

    @patch("app.client.azure_openai_client.azure_openai_settings")
    def test_get_azure_openai_completion(self, mock_settings):
        """Test get completion function."""
        # Setup
        mock_settings.gpt4o_deployment_name = "gpt-4o-deployment"
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = {
            "choices": [{"message": {"content": "Test response"}}]
        }

        messages = [{"role": "user", "content": "Hello"}]

        # Execute
        result = get_azure_openai_completion(
            client=mock_client, model_name="gpt-4o", messages=messages, temperature=0.5
        )

        # Verify
        mock_client.chat.completions.create.assert_called_once_with(
            model="gpt-4o-deployment",
            messages=messages,
            temperature=0.5,
            max_tokens=None,
            stream=False,
        )
        self.assertEqual(result, mock_client.chat.completions.create.return_value)

    @patch("app.client.azure_openai_client.azure_openai_settings")
    def test_get_azure_openai_completion_invalid_model(self, mock_settings):
        """Test get completion with invalid model."""
        # Setup
        mock_client = MagicMock()
        messages = [{"role": "user", "content": "Hello"}]

        # Execute and verify
        with self.assertRaises(ModelNotAvailableError):
            get_azure_openai_completion(
                client=mock_client, model_name="invalid-model", messages=messages
            )

    @patch("app.client.azure_openai_client.azure_openai_settings")
    def test_get_azure_openai_embedding(self, mock_settings):
        """Test get embedding function."""
        # Setup
        mock_settings.embedding_deployment_name = "text-embedding-3-small-deployment"
        mock_client = MagicMock()

        # Mock the embeddings response
        mock_embedding = MagicMock()
        mock_embedding.embedding = [0.1, 0.2, 0.3]

        mock_response = MagicMock()
        mock_response.data = [mock_embedding]

        mock_client.embeddings.create.return_value = mock_response

        texts = ["Test text"]

        # Execute
        result = get_azure_openai_embedding(client=mock_client, texts=texts)

        # Verify
        mock_client.embeddings.create.assert_called_once_with(
            model="text-embedding-3-small-deployment",
            input=texts,
        )
        self.assertEqual(result, [[0.1, 0.2, 0.3]])

    def test_get_available_models(self):
        """Test get available models function."""
        # Setup
        mock_client = MagicMock()

        deployment1 = MagicMock()
        deployment1.model = "gpt-4o"

        deployment2 = MagicMock()
        deployment2.model = "text-embedding-3-small"

        mock_client.deployments.list.return_value = [deployment1, deployment2]

        # Execute
        result = get_available_models(mock_client)

        # Verify
        self.assertEqual(result, ["gpt-4o", "text-embedding-3-small"])

    def test_client_pool(self):
        """Test Azure OpenAI client pool."""
        # Setup
        with patch(
            "app.client.azure_openai_client.get_azure_openai_client"
        ) as mock_get_client:
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client

            # Execute
            pool = AzureOpenAIClientPool(pool_size=3)
            pool.initialize()

            # Verify
            self.assertEqual(mock_get_client.call_count, 3)
            self.assertEqual(len(pool.clients), 3)

            # Test round-robin behavior
            self.assertEqual(pool.get_client(), mock_client)
            self.assertEqual(pool.get_client(), mock_client)
            self.assertEqual(pool.get_client(), mock_client)
            # Should wrap around
            self.assertEqual(pool.get_client(), mock_client)


if __name__ == "__main__":
    unittest.main()
