"""Environment and application settings."""

from typing import Dict, List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable configuration."""

    # Environment settings
    ENV_MODE: str = "development"

    # Azure OpenAI Settings
    AZURE_OPENAI_API_KEY: str = Field(..., description="Azure OpenAI API key")
    AZURE_OPENAI_ENDPOINT: str = Field(..., description="Azure OpenAI endpoint URL")
    AZURE_OPENAI_API_VERSION: str = Field(
        "2023-05-15", description="Azure OpenAI API version"
    )

    # Model deployments
    AZURE_OPENAI_GPT4O_DEPLOYMENT: str = Field(
        ..., description="Azure OpenAI GPT-4o deployment name"
    )
    AZURE_OPENAI_GPT4O_MINI_DEPLOYMENT: Optional[str] = Field(
        None, description="Azure OpenAI GPT-4o mini deployment name (optional)"
    )
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: Optional[str] = Field(
        None, description="Azure OpenAI embedding model deployment name"
    )

    # Compatibility with standard OpenAI settings
    OPENAI_API_KEY: Optional[str] = Field(None, description="Standard OpenAI API key")
    OPENAI_API_BASE: Optional[str] = Field(
        None, description="Standard OpenAI API base URL"
    )
    OPENAI_API_VERSION: Optional[str] = Field(
        None, description="Standard OpenAI API version"
    )

    # LangSmith Settings
    LANGCHAIN_TRACING_V2: bool = Field(False, description="Enable LangSmith tracing V2")
    LANGCHAIN_API_KEY: Optional[str] = Field(
        None, description="LangChain/LangSmith API key"
    )
    LANGCHAIN_PROJECT: str = Field(
        "lg-playground", description="LangSmith project name"
    )

    # FastAPI Settings
    APP_NAME: str = Field("LangGraph Playground", description="Application name")
    API_DEBUG: bool = Field(False, description="Enable API debug mode")
    API_TITLE: str = Field("LangGraph Playground API", description="API title")
    API_VERSION: str = Field("0.1.0", description="API version")
    DEBUG: bool = Field(False, description="Debug mode")

    # CORS Settings
    CORS_ORIGINS: List[str] = Field(
        ["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins",
    )

    @field_validator("ENV_MODE")
    @classmethod
    def validate_env_mode(cls, v: str) -> str:
        """Validate environment mode."""
        valid_modes = ["development", "testing", "production"]
        if v.lower() not in valid_modes:
            raise ValueError(f"ENV_MODE must be one of {', '.join(valid_modes)}")
        return v.lower()

    def get_openai_credentials(self) -> Dict[str, str]:
        """Get Azure OpenAI credentials as dictionary."""
        return {
            "api_key": self.AZURE_OPENAI_API_KEY,
            "api_base": self.AZURE_OPENAI_ENDPOINT,
            "api_version": self.AZURE_OPENAI_API_VERSION,
        }

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",  # Allow extra fields to handle various environment variables
    )


# Create settings instance
settings = Settings()
