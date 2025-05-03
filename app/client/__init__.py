"""Client initialization package."""

from app.client.elasticsearch_client import get_elasticsearch_client
from app.client.azure_openai_client import (
    get_azure_openai_client,
    get_azure_openai_completion,
    get_azure_openai_embedding,
    get_available_models,
    AzureOpenAIClientPool,
    ModelNotAvailableError,
)

__all__ = [
    "get_elasticsearch_client",
    "get_azure_openai_client",
    "get_azure_openai_completion",
    "get_azure_openai_embedding",
    "get_available_models",
    "AzureOpenAIClientPool",
    "ModelNotAvailableError",
]
