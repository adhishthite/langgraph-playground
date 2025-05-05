"""Azure OpenAI client setup and management."""

import logging
from typing import Optional, Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings, ChatOpenAI
from openai import APIConnectionError, APIError, RateLimitError

from app.config.settings import settings

logger = logging.getLogger(__name__)


class OpenAIClientError(Exception):
    """Exception raised for errors in OpenAI client interactions."""

    pass


def get_azure_chat_model(
    deployment_name: str,
    temperature: float = 0.0,
    streaming: bool = True,
    max_retries: int = 3,
    **kwargs: Any,
) -> AzureChatOpenAI:
    """
    Create an Azure OpenAI chat model client with the specified configuration.

    Args:
        deployment_name: The Azure deployment name
        temperature: The temperature for generation
        streaming: Whether to stream responses
        max_retries: Maximum number of retries for API errors
        **kwargs: Additional parameters for the AzureChatOpenAI constructor

    Returns:
        AzureChatOpenAI: The configured Azure OpenAI client

    Raises:
        OpenAIClientError: If the client cannot be created
    """
    try:
        return AzureChatOpenAI(
            azure_deployment=deployment_name,
            openai_api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            openai_api_key=settings.AZURE_OPENAI_API_KEY,
            temperature=temperature,
            streaming=streaming,
            max_retries=max_retries,
            **kwargs,
        )
    except Exception as e:
        logger.error(f"Failed to create Azure OpenAI client: {str(e)}")
        raise OpenAIClientError(
            f"Failed to create Azure OpenAI client: {str(e)}"
        ) from e


def get_embedding_model(
    deployment_name: Optional[str] = None,
    max_retries: int = 3,
    **kwargs: Any,
) -> AzureOpenAIEmbeddings:
    """
    Create an Azure OpenAI embeddings client.

    Args:
        deployment_name: The Azure deployment name (defaults to setting)
        max_retries: Maximum number of retries for API errors
        **kwargs: Additional parameters for the AzureOpenAIEmbeddings constructor

    Returns:
        AzureOpenAIEmbeddings: The configured embeddings client

    Raises:
        OpenAIClientError: If the client cannot be created
        ValueError: If the embedding deployment is not configured
    """
    deployment = deployment_name or settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT

    if not deployment:
        raise ValueError("Azure OpenAI embedding deployment not configured")

    try:
        return AzureOpenAIEmbeddings(
            azure_deployment=deployment,
            openai_api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            openai_api_key=settings.AZURE_OPENAI_API_KEY,
            max_retries=max_retries,
            **kwargs,
        )
    except Exception as e:
        logger.error(f"Failed to create Azure embeddings client: {str(e)}")
        raise OpenAIClientError(
            f"Failed to create Azure embeddings client: {str(e)}"
        ) from e


def get_model(
    model_name: str,
    temperature: float = 0.0,
    streaming: bool = True,
    **kwargs: Any,
) -> BaseChatModel:
    """
    Get a model by name with specified parameters.

    Args:
        model_name: The model name or alias
        temperature: The temperature for generation
        streaming: Whether to stream responses
        **kwargs: Additional parameters for the client constructor

    Returns:
        BaseChatModel: The configured chat model client

    Raises:
        ValueError: If the model name is unknown
    """
    # Map model names to Azure deployments
    model_map = {
        "gpt-4o": settings.AZURE_OPENAI_GPT4O_DEPLOYMENT,
        "gpt-4o-mini": settings.AZURE_OPENAI_GPT4O_MINI_DEPLOYMENT,
        "gpt-4": settings.AZURE_OPENAI_GPT4O_DEPLOYMENT,  # Map gpt-4 to gpt-4o deployment for testing
        # Add more model mappings as needed
    }

    # Check if we should use Azure OpenAI
    if settings.AZURE_OPENAI_ENDPOINT and settings.AZURE_OPENAI_API_KEY:
        # If using Azure deployment name directly, use it
        if model_name in [
            settings.AZURE_OPENAI_GPT4O_DEPLOYMENT,
            settings.AZURE_OPENAI_GPT4O_MINI_DEPLOYMENT,
        ]:
            deployment = model_name
        else:
            # Try to map to deployment
            deployment = model_map.get(model_name)

        if not deployment:
            raise ValueError(f"Unknown model name for Azure: {model_name}")

        return get_azure_chat_model(
            deployment,
            temperature=temperature,
            streaming=streaming,
            **kwargs,
        )

    # Fallback to standard OpenAI
    elif settings.OPENAI_API_KEY:
        logger.info(f"Using standard OpenAI API with model: {model_name}")
        return ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model_name=model_name,
            temperature=temperature,
            streaming=streaming,
            **kwargs,
        )

    else:
        raise ValueError("No OpenAI credentials configured")


def handle_api_error(func):
    """
    Decorator for handling OpenAI API errors.

    Args:
        func: The function to wrap

    Returns:
        The wrapped function with error handling
    """
    import functools

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except RateLimitError as e:
            logger.warning(f"OpenAI rate limit exceeded: {e}")
            raise OpenAIClientError(f"Rate limit exceeded: {e}") from e
        except APIConnectionError as e:
            logger.error(f"OpenAI API connection error: {e}")
            raise OpenAIClientError(f"API connection error: {e}") from e
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise OpenAIClientError(f"API error: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI client: {e}")
            raise OpenAIClientError(f"Unexpected error: {e}") from e

    return wrapper


# Initialize default clients for easy access
try:
    default_chat_model = get_azure_chat_model(settings.AZURE_OPENAI_GPT4O_DEPLOYMENT)
    logger.info("Initialized default Azure OpenAI chat model")

    if (
        hasattr(settings, "AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
        and settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT
    ):
        default_embedding_model = get_embedding_model()
        logger.info("Initialized default Azure embedding model")
    else:
        default_embedding_model = None
        logger.warning("No embedding model deployment configured")

except Exception as e:
    logger.warning(f"Could not initialize default models: {e}")
    default_chat_model = None
    default_embedding_model = None
