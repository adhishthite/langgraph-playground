# 002-TASK: Settings Configuration

## Overview
Create a settings module that loads environment variables and provides configuration for the entire application, following best practices for configuration management using Pydantic.

## Requirements
- Use `pydantic-settings` for environment variable validation and loading
- Support different environment modes (development, testing, production)
- Configure Azure OpenAI API integration settings
- Set up LangSmith API settings for observability
- Include FastAPI configuration options
- Provide sensible defaults where appropriate

## Implementation Details

### Settings Structure
- Create `app/config/settings.py` with Pydantic Settings classes
- Implement environment variable loading with proper validation 
- Include required Azure OpenAI settings:
  - API key
  - API base URL
  - API version
  - Available model deployments
- Add LangSmith settings:
  - API key
  - API URL
  - Project name
  - Tracing configuration
- Include FastAPI settings:
  - Debug mode
  - CORS configuration
  - Title and version information

### Environment Variables
- Create `.env.example` file with all required variables
- Document all environment variables in the README
- Ensure secrets are properly handled (not committed to repository)

## Code Structure

```python
# Example structure for settings.py
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Dict, List, Optional

class Settings(BaseSettings):
    # Environment settings
    ENV_MODE: str = "development"
    
    # Azure OpenAI Settings
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_API_VERSION: str = "2023-05-15"
    
    # Model deployments
    AZURE_OPENAI_GPT4O_DEPLOYMENT: str
    AZURE_OPENAI_GPT4O_MINI_DEPLOYMENT: Optional[str] = None
    
    # LangSmith Settings
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: str = "lg-playground"
    
    # FastAPI Settings
    API_DEBUG: bool = False
    API_TITLE: str = "LangGraph Playground"
    API_VERSION: str = "0.1.0"
    
    # Model field validators and computed fields
    # ...

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

# Create settings instance
settings = Settings()
```

## Success Criteria
- All required environment variables are properly loaded and validated
- Documentation clearly explains required environment variables
- The settings module provides a central place for application configuration
- Different deployment environments can be easily configured
- Secret keys and sensitive information are handled securely