"""Mock settings for tests."""


class MockSettings:
    """Mock settings class for tests."""

    AZURE_OPENAI_API_KEY = "test-key"
    AZURE_OPENAI_ENDPOINT = "https://test-endpoint.openai.azure.com"
    AZURE_OPENAI_API_VERSION = "2023-05-15"
    AZURE_OPENAI_GPT4O_DEPLOYMENT = "test-deployment"
    AZURE_OPENAI_GPT4O_MINI_DEPLOYMENT = "test-mini-deployment"
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT = "test-embedding-deployment"
    OPENAI_API_KEY = None
    OPENAI_API_BASE = None
    OPENAI_API_VERSION = None


# Mock instance
settings = MockSettings()
