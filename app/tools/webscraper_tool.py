"""Web scraping tool."""

import httpx
from typing import Dict, Any, Optional

from langchain_core.tools import tool
from bs4 import BeautifulSoup


@tool
async def scrape_webpage(url: str, selector: Optional[str] = None) -> Dict[str, Any]:
    """Scrape content from a webpage.

    Args:
        url: The URL to scrape
        selector: Optional CSS selector to extract specific content

    Returns:
        Dictionary with title, text content, and optional selected content
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract title
        title = soup.title.string if soup.title else "No title found"

        # Extract text content
        text_content = " ".join([p.text for p in soup.find_all("p")])

        result = {
            "title": title,
            "text_content": (
                text_content[:500] + "..." if len(text_content) > 500 else text_content
            ),
            "url": url,
        }

        # Extract selected content if selector is provided
        if selector:
            selected = soup.select(selector)
            if selected:
                selected_content = "\n".join([el.text.strip() for el in selected])
                result["selected_content"] = selected_content
            else:
                result["selected_content"] = (
                    "No content found with the provided selector."
                )

        return result
    except Exception as e:
        return {"error": f"Failed to scrape {url}: {str(e)}"}
