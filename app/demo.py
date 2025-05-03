# ruff: noqa: E402
"""
Demo script to show configuration settings in action.

This script loads the application settings and displays them.
It validates that all required settings are present and tests
the Elasticsearch client connection.
"""

import sys
from pathlib import Path
import os

# Add the project root directory to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config.settings import settings
from app.client import get_elasticsearch_client

from rich.console import Console
from rich.table import Table

console = Console()


def main():
    """Display configuration settings and validate them."""
    console.print("[bold green]SmartSource RAG Agent - Configuration Demo[/bold green]")
    console.print()

    try:
        # Validate required settings
        settings.validate_required_settings()

        # Azure OpenAI settings
        azure_table = Table(title="Azure OpenAI Settings")
        azure_table.add_column("Setting", style="cyan")
        azure_table.add_column("Value", style="green")

        azure_table.add_row("Endpoint", settings.azure_openai.endpoint)
        azure_table.add_row("API Version", settings.azure_openai.api_version)
        azure_table.add_row("GPT-4o Model", settings.azure_openai.gpt4o_deployment_name)
        azure_table.add_row(
            "Embeddings Model", settings.azure_openai.embedding_deployment_name
        )
        console.print(azure_table)
        console.print()

        # LangSmith settings
        langsmith_table = Table(title="LangSmith Settings")
        langsmith_table.add_column("Setting", style="cyan")
        langsmith_table.add_column("Value", style="green")

        langsmith_table.add_row(
            "Tracing Enabled", str(settings.langsmith.tracing_enabled)
        )
        langsmith_table.add_row("Endpoint", settings.langsmith.endpoint)
        langsmith_table.add_row("Project", settings.langsmith.project)
        console.print(langsmith_table)
        console.print()

        # Elasticsearch settings
        es_table = Table(title="Elasticsearch Settings")
        es_table.add_column("Setting", style="cyan")
        es_table.add_column("Value", style="green")

        es_table.add_row("Host", settings.elasticsearch.host)
        es_table.add_row("Indices", ", ".join(settings.elasticsearch.index_names))
        
        # Check for API key (existence only, not its value)
        api_key_status = "[green]Configured[/green]" if os.environ.get("ES_API_KEY") else "[red]Not configured[/red]"
        es_table.add_row("API Key", api_key_status)
        
        console.print(es_table)
        console.print()

        # Service settings
        service_table = Table(title="Service Settings")
        service_table.add_column("Setting", style="cyan")
        service_table.add_column("Value", style="green")

        service_table.add_row("Log Level", settings.service.log_level.value)
        service_table.add_row("Default Agent", settings.service.default_agent)
        service_table.add_row(
            "Max Document Count", str(settings.service.max_document_count)
        )
        service_table.add_row("RRF K Factor", str(settings.service.rrf_k_factor))
        console.print(service_table)
        console.print()
        
        # Test Elasticsearch connection
        try:
            es_client = get_elasticsearch_client()
            if es_client and es_client.ping():
                console.print("[bold green]Elasticsearch Connection:[/bold green] Successfully connected!")
                # Get cluster info without showing sensitive data
                info = es_client.info()
                console.print(f"Cluster Name: {info.get('cluster_name', 'N/A')}")
                console.print(f"Elasticsearch Version: {info.get('version', {}).get('number', 'N/A')}")
            else:
                console.print("[bold yellow]Elasticsearch Connection:[/bold yellow] Not connected")
        except Exception as e:
            console.print(f"[bold red]Elasticsearch Connection Error:[/bold red] {str(e)}")

        console.print("[bold green]Configuration validated successfully![/bold green]")
        return 0

    except ValueError as e:
        console.print(f"[bold red]Configuration Error:[/bold red] {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
