"""
Configuration settings for the SmartSource RAG Agent.

This module loads environment variables and provides validated configuration
settings for the application using Pydantic.

Import settings directly:
    from app.config import settings
    from app.config import azure_openai_settings
"""

import os
from enum import Enum
from typing import List, Optional, Any

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load environment variables from .env file
load_dotenv()


class LogLevel(str, Enum):
    """Valid logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AzureOpenAISettings(BaseModel):
    """Azure OpenAI API configuration settings."""

    api_key: str = ""  # Default empty for testing
    endpoint: str = ""  # Default empty for testing
    api_version: str = "2024-02-15-preview"

    # Model deployments
    gpt4o_deployment_name: str = "gpt-4o"
    gpt4o_mini_deployment_name: str = "gpt-4o-mini"
    gpt41_deployment_name: str = "gpt-4.1"
    gpt41_mini_deployment_name: str = "gpt-4.1-mini"
    gpt41_nano_deployment_name: str = "gpt-4.1-nano"
    embedding_deployment_name: str = "text-embedding-3-small"


class ElasticsearchSettings(BaseModel):
    """Elasticsearch configuration settings."""

    host: str = "localhost"
    port: int = 9200
    user: Optional[str] = None
    password: Optional[str] = None
    index_names: List[str] = []

    @field_validator("index_names", mode="before")
    @classmethod
    def split_index_names(cls, v: Any) -> Any:
        """Convert comma-separated index names to a list."""
        if isinstance(v, str):
            return [x.strip() for x in v.split(",")]
        return v


class LangSmithSettings(BaseModel):
    """LangSmith tracing configuration."""

    tracing_enabled: bool = True
    endpoint: str = "https://api.smith.langchain.com"
    api_key: Optional[str] = None
    project: str = "langgraph-playground"


class ServiceSettings(BaseModel):
    """General application settings."""

    log_level: LogLevel = LogLevel.INFO
    default_agent: str = "smartsource"
    max_document_count: int = 5
    rrf_k_factor: float = 60.0


class Settings(BaseSettings):
    """Main application settings."""

    # Configuration sources
    model_config = SettingsConfigDict(
        env_file=["../.env", ".env"],  # Look in both project root and current directory
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    # Service components
    azure_openai: AzureOpenAISettings = Field(default_factory=AzureOpenAISettings)
    elasticsearch: ElasticsearchSettings = Field(default_factory=ElasticsearchSettings)
    langsmith: LangSmithSettings = Field(default_factory=LangSmithSettings)
    service: ServiceSettings = Field(default_factory=ServiceSettings)

    @field_validator("azure_openai", mode="before")
    @classmethod
    def validate_azure_openai(cls, v: Any) -> Any:
        """Ensure Azure OpenAI settings are properly configured."""
        if isinstance(v, dict):
            return v

        return {
            "api_key": os.environ.get("AZURE_OPENAI_API_KEY"),
            "endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
            "api_version": os.environ.get(
                "AZURE_OPENAI_API_VERSION", "2024-02-15-preview"
            ),
            "gpt4o_deployment_name": os.environ.get("GPT4O_DEPLOYMENT_NAME", "gpt-4o"),
            "gpt4o_mini_deployment_name": os.environ.get(
                "GPT4O_MINI_DEPLOYMENT_NAME", "gpt-4o-mini"
            ),
            "gpt41_deployment_name": os.environ.get("GPT41_DEPLOYMENT_NAME", "gpt-4.1"),
            "gpt41_mini_deployment_name": os.environ.get(
                "GPT41_MINI_DEPLOYMENT_NAME", "gpt-4.1-mini"
            ),
            "gpt41_nano_deployment_name": os.environ.get(
                "GPT41_NANO_DEPLOYMENT_NAME", "gpt-4.1-nano"
            ),
            "embedding_deployment_name": os.environ.get(
                "EMBEDDING_DEPLOYMENT_NAME", "text-embedding-3-small"
            ),
        }

    @field_validator("elasticsearch", mode="before")
    @classmethod
    def validate_elasticsearch(cls, v: Any) -> Any:
        """Configure Elasticsearch settings from environment variables."""
        if isinstance(v, dict):
            return v

        # Note: Modern Elasticsearch hosts typically include the port in the host URL
        # e.g., https://my-deployment.es.amazonaws.com:9243
        return {
            "host": os.environ.get("ES_HOST", "localhost"),
            "port": 9200,  # Default port, modern ES URLs often include the port in the host
            "user": os.environ.get("ES_USER"),
            "password": os.environ.get("ES_PASSWORD"),
            "index_names": os.environ.get("ES_INDEX_NAMES", ""),
        }

    @field_validator("langsmith", mode="before")
    @classmethod
    def validate_langsmith(cls, v: Any) -> Any:
        """Configure LangSmith settings from environment variables."""
        if isinstance(v, dict):
            return v

        return {
            "tracing_enabled": os.environ.get("LANGSMITH_TRACING", "true").lower()
            == "true",
            "endpoint": os.environ.get(
                "LANGSMITH_ENDPOINT", "https://api.smith.langchain.com"
            ),
            "api_key": os.environ.get("LANGSMITH_API_KEY"),
            "project": os.environ.get("LANGSMITH_PROJECT", "smartsource-rag-agent"),
        }

    @field_validator("service", mode="before")
    @classmethod
    def validate_service(cls, v: Any) -> Any:
        """Configure general service settings from environment variables."""
        if isinstance(v, dict):
            return v

        return {
            "log_level": os.environ.get("LOG_LEVEL", "INFO"),
            "default_agent": os.environ.get("DEFAULT_AGENT", "smartsource"),
            "max_document_count": int(os.environ.get("MAX_DOCUMENT_COUNT", "5")),
            "rrf_k_factor": float(os.environ.get("RRF_K_FACTOR", "60.0")),
        }

    def validate_required_settings(self):
        """Validate that all required settings are present."""
        missing = []

        # Validate Azure OpenAI settings
        if not self.azure_openai.api_key:
            missing.append("AZURE_OPENAI_API_KEY")
        if not self.azure_openai.endpoint:
            missing.append("AZURE_OPENAI_ENDPOINT")

        # Validate LangSmith settings if tracing is enabled
        if self.langsmith.tracing_enabled and not self.langsmith.api_key:
            missing.append("LANGSMITH_API_KEY")

        # Validate Elasticsearch credentials if provided
        if (self.elasticsearch.user and not self.elasticsearch.password) or (
            not self.elasticsearch.user and self.elasticsearch.password
        ):
            missing.append(
                "Both ES_USER and ES_PASSWORD must be provided if one is set"
            )

        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"
            )

        return True


# Create settings instance in a try-except block to handle test environments
# where environment variables might not be set
try:
    settings = Settings()
    # Export settings for easy import
    azure_openai_settings = settings.azure_openai
    elasticsearch_settings = settings.elasticsearch
    langsmith_settings = settings.langsmith
    service_settings = settings.service
except Exception:
    # These will be None in test environments
    settings = None
    azure_openai_settings = None
    elasticsearch_settings = None
    langsmith_settings = None
    service_settings = None
