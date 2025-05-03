"""
Configuration module for the SmartSource RAG Agent.

This module provides configuration settings and validation for the application.
"""

# Import the Settings class and settings instances for direct access
from app.config.settings import (
    Settings, 
    settings, 
    azure_openai_settings, 
    elasticsearch_settings,
    langsmith_settings, 
    service_settings
)

# Make all settings accessible from the package
__all__ = [
    "Settings",
    "settings",
    "azure_openai_settings", 
    "elasticsearch_settings",
    "langsmith_settings",
    "service_settings"
]
