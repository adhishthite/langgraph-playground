"""Client initialization package."""

from app.client.elasticsearch_client import get_elasticsearch_client

__all__ = ["get_elasticsearch_client"]