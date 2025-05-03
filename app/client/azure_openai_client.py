"""
Azure OpenAI client module for the SmartSource RAG Agent.

This module initializes the Azure OpenAI client using configuration settings,
handles authentication, model selection, and provides error handling.
"""

import logging
from typing import Dict, List, Optional, Union, Any

from openai import AzureOpenAI, APIError, RateLimitError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)
from app.config import azure_openai_settings

# Set up logging
logger = logging.getLogger(__name__)


class ModelNotAvailableError(Exception):
    """Raised when a requested model is not available."""

    pass


def get_azure_openai_client() -> Optional[AzureOpenAI]:
    """
    Initialize and return an Azure OpenAI client.

    Uses the environment variables loaded through settings.
    Never hardcodes sensitive information.

    Returns:
        AzureOpenAI: Configured Azure OpenAI client or None if not configured
    """
    # Only initialize if we have settings available (may be None in tests)
    if not azure_openai_settings:
        return None

    # Check for required settings
    if not azure_openai_settings.api_key or not azure_openai_settings.endpoint:
        logger.warning("Azure OpenAI API key or endpoint not configured.")
        return None

    # Create the client
    client = AzureOpenAI(
        api_key=azure_openai_settings.api_key,
        azure_endpoint=azure_openai_settings.endpoint,
        api_version=azure_openai_settings.api_version,
    )

    return client


# Dictionary mapping model types to their deployment names
MODEL_DEPLOYMENT_MAP = {
    "gpt-4o": lambda: azure_openai_settings.gpt4o_deployment_name,
    "gpt-4o-mini": lambda: azure_openai_settings.gpt4o_mini_deployment_name,
    "gpt-4.1": lambda: azure_openai_settings.gpt41_deployment_name,
    "gpt-4.1-mini": lambda: azure_openai_settings.gpt41_mini_deployment_name,
    "gpt-4.1-nano": lambda: azure_openai_settings.gpt41_nano_deployment_name,
    "text-embedding-3-small": lambda: azure_openai_settings.embedding_deployment_name,
}


@retry(
    retry=retry_if_exception_type((APIError, RateLimitError)),
    wait=wait_exponential(multiplier=1, min=2, max=60),
    stop=stop_after_attempt(5),
    before_sleep=before_sleep_log(logger, logging.WARNING),
)
def get_azure_openai_completion(
    client: AzureOpenAI,
    model_name: str,
    messages: List[Dict[str, str]],
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    stream: bool = False,
    **kwargs: Any,
) -> Union[Dict[str, Any], Any]:
    """
    Get a completion from Azure OpenAI with retry logic for reliability.

    Args:
        client: The Azure OpenAI client instance
        model_name: The base model name to use (e.g., "gpt-4o")
        messages: The messages to send to the model
        temperature: Controls randomness (0-1)
        max_tokens: Maximum tokens to generate
        stream: Whether to stream the response
        **kwargs: Additional arguments to pass to the completion call

    Returns:
        The completion response

    Raises:
        ModelNotAvailableError: If the requested model is not available
        APIError: If there's an API error after retries
    """
    if not client:
        raise ValueError("Azure OpenAI client not initialized")

    # Get the deployment name for the model
    deployment_name_func = MODEL_DEPLOYMENT_MAP.get(model_name)
    if not deployment_name_func:
        raise ModelNotAvailableError(f"Model '{model_name}' not configured")

    deployment_name = deployment_name_func()
    if not deployment_name:
        raise ModelNotAvailableError(
            f"Deployment for model '{model_name}' not configured"
        )

    try:
        # Make the completion request
        response = client.chat.completions.create(
            model=deployment_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            **kwargs,
        )
        return response
    except RateLimitError:
        logger.warning(f"Rate limit hit for model {model_name}. Retrying...")
        # This will be retried by the @retry decorator
        raise
    except APIError as e:
        logger.warning(f"API error when calling {model_name}: {str(e)}. Retrying...")
        # This will be retried by the @retry decorator
        raise
    except Exception as e:
        logger.error(f"Error in OpenAI completion for {model_name}: {str(e)}")
        raise


@retry(
    retry=retry_if_exception_type((APIError, RateLimitError)),
    wait=wait_exponential(multiplier=1, min=2, max=60),
    stop=stop_after_attempt(5),
    before_sleep=before_sleep_log(logger, logging.WARNING),
)
def get_azure_openai_embedding(
    client: AzureOpenAI, texts: List[str], model_name: str = "text-embedding-3-small"
) -> List[List[float]]:
    """
    Get embeddings from Azure OpenAI with retry logic for reliability.

    Args:
        client: The Azure OpenAI client instance
        texts: List of texts to embed
        model_name: The embedding model to use

    Returns:
        List of embedding vectors

    Raises:
        ModelNotAvailableError: If the requested model is not available
        APIError: If there's an API error after retries
    """
    if not client:
        raise ValueError("Azure OpenAI client not initialized")

    # Get the deployment name for the embedding model
    deployment_name_func = MODEL_DEPLOYMENT_MAP.get(model_name)
    if not deployment_name_func:
        raise ModelNotAvailableError(f"Embedding model '{model_name}' not configured")

    deployment_name = deployment_name_func()
    if not deployment_name:
        raise ModelNotAvailableError(
            f"Deployment for embedding model '{model_name}' not configured"
        )

    try:
        response = client.embeddings.create(
            model=deployment_name,
            input=texts,
        )
        # Extract the embedding vectors from the response
        embeddings = [item.embedding for item in response.data]
        return embeddings
    except RateLimitError:
        logger.warning(f"Rate limit hit for embedding model {model_name}. Retrying...")
        # This will be retried by the @retry decorator
        raise
    except APIError as e:
        logger.warning(
            f"API error when calling embedding model {model_name}: {str(e)}. Retrying..."
        )
        # This will be retried by the @retry decorator
        raise
    except Exception as e:
        logger.error(f"Error in OpenAI embedding for {model_name}: {str(e)}")
        raise


def get_available_models(client: AzureOpenAI) -> List[str]:
    """
    Get a list of available model deployments.

    Args:
        client: The Azure OpenAI client

    Returns:
        List of available model deployment names
    """
    if not client:
        return []

    try:
        # Get all deployments from the Azure OpenAI API
        deployments = client.deployments.list()
        return [deployment.model for deployment in deployments]
    except Exception as e:
        logger.error(f"Error retrieving available models: {str(e)}")
        return []


class AzureOpenAIClientPool:
    """
    A simple client pooling mechanism for Azure OpenAI clients.

    This helps manage multiple client instances for performance.
    """

    def __init__(self, pool_size: int = 5):
        """
        Initialize the client pool.

        Args:
            pool_size: Maximum number of clients in the pool
        """
        self.pool_size = pool_size
        self.clients: List[AzureOpenAI] = []
        self.current_index = 0

    def initialize(self) -> None:
        """Initialize the client pool."""
        for _ in range(self.pool_size):
            client = get_azure_openai_client()
            if client:
                self.clients.append(client)

    def get_client(self) -> Optional[AzureOpenAI]:
        """
        Get a client from the pool in a round-robin fashion.

        Returns:
            An Azure OpenAI client or None if the pool is empty
        """
        if not self.clients:
            # Initialize if not already done
            self.initialize()

        if not self.clients:
            # Still no clients available
            return None

        # Round-robin selection
        client = self.clients[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.clients)
        return client
