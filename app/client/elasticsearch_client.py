"""
Elasticsearch client module for the SmartSource RAG Agent.

This module initializes the Elasticsearch client using configuration settings.
"""

from typing import Optional

from elasticsearch import Elasticsearch
from app.config import elasticsearch_settings


def get_elasticsearch_client() -> Optional[Elasticsearch]:
    """
    Initialize and return an Elasticsearch client.

    Uses the environment variables loaded through settings.
    Never hardcodes sensitive information.

    Returns:
        Elasticsearch: Configured Elasticsearch client or None if not configured
    """
    # Only initialize if we have settings available (may be None in tests)
    if not elasticsearch_settings:
        return None

    # Initialize authentication based on what's available
    auth = None
    if elasticsearch_settings.user and elasticsearch_settings.password:
        auth = (elasticsearch_settings.user, elasticsearch_settings.password)

    # Additional options for connecting to Elasticsearch with API key
    es_options = {
        "verify_certs": True,
        "request_timeout": 30,
    }

    # Get API key from environment if available
    api_key = None
    import os

    es_api_key = os.environ.get("ES_API_KEY")
    if es_api_key:
        api_key = es_api_key

    # Create client - modern Elasticsearch hosts include the port in the URL
    # e.g., https://my-deployment.es.amazonaws.com:9243
    client = Elasticsearch(
        hosts=[
            elasticsearch_settings.host
        ],  # Use host directly as it includes port if needed
        basic_auth=auth,
        api_key=api_key,
        **es_options,
    )

    return client
