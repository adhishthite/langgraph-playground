# 003-TASK: Azure OpenAI Integration

## Overview
Create a module that handles Azure OpenAI client initialization and management, providing a consistent interface for model access throughout the application.

## Requirements
- Create integration with Azure OpenAI API
- Support multiple model deployments (GPT-4o, GPT-4o-mini, etc.)
- Configure proper API version handling
- Implement embedding model configuration
- Ensure proper error handling for API requests
- Make clients available to other application components

## Implementation Details

### Module Structure
Create `app/core/llm_clients.py` to initialize and manage Azure OpenAI clients:

```python
# Example structure
from typing import Dict, Optional
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from app.config.settings import settings

def get_azure_chat_model(
    deployment_name: str,
    temperature: float = 0.0,
    streaming: bool = True,
) -> AzureChatOpenAI:
    """
    Create an Azure OpenAI chat model client with the specified configuration.
    """
    return AzureChatOpenAI(
        azure_deployment=deployment_name,
        openai_api_version=settings.AZURE_OPENAI_API_VERSION,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        openai_api_key=settings.AZURE_OPENAI_API_KEY,
        temperature=temperature,
        streaming=streaming,
    )

def get_embedding_model() -> AzureOpenAIEmbeddings:
    """
    Create an Azure OpenAI embeddings client.
    """
    return AzureOpenAIEmbeddings(
        azure_deployment=settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
        openai_api_version=settings.AZURE_OPENAI_API_VERSION,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        openai_api_key=settings.AZURE_OPENAI_API_KEY,
    )

# Factory function for getting appropriate model based on name or requirements
def get_model(model_name: str, **kwargs) -> AzureChatOpenAI:
    """
    Get a model by name with specified parameters.
    """
    model_map = {
        "gpt-4o": settings.AZURE_OPENAI_GPT4O_DEPLOYMENT,
        "gpt-4o-mini": settings.AZURE_OPENAI_GPT4O_MINI_DEPLOYMENT,
        # Additional mappings
    }
    
    deployment = model_map.get(model_name)
    if not deployment:
        raise ValueError(f"Unknown model name: {model_name}")
        
    return get_azure_chat_model(deployment, **kwargs)

# Initialize default clients for easy access
default_chat_model = get_azure_chat_model(settings.AZURE_OPENAI_GPT4O_DEPLOYMENT)
default_embedding_model = get_embedding_model()
```

### Error Handling
- Implement error handling for API key errors, network issues, and rate limits
- Create retry logic for common failure modes
- Provide useful error messages for debugging

## Success Criteria
- Azure OpenAI clients are properly initialized with settings from environment variables
- Different model deployments can be accessed through a consistent interface
- Error handling is robust and provides useful diagnostics
- The interface is consistent and easy to use from agent implementations
- Changes to Azure OpenAI API versions can be managed through configuration