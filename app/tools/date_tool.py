"""Date/time information tool."""

from datetime import datetime
from typing import Dict, Any

from langchain_core.tools import tool


@tool
def get_current_date(tool_input: str = None) -> str:
    """Get the current date and time.

    Args:
        tool_input: Optional input (not used)

    Returns:
        The current date and time as an ISO format string
    """
    return datetime.now().isoformat()


@tool
def parse_date(date_string: str, tool_input: str = None) -> Dict[str, Any]:
    """Parse a date string into components.

    Args:
        date_string: A string representing a date (e.g., "2023-04-25")
        tool_input: Optional input (not used)

    Returns:
        A dictionary containing the parsed date components
    """
    try:
        date_obj = datetime.fromisoformat(date_string)
        return {
            "year": date_obj.year,
            "month": date_obj.month,
            "day": date_obj.day,
            "hour": date_obj.hour,
            "minute": date_obj.minute,
            "second": date_obj.second,
            "weekday": date_obj.strftime("%A"),
        }
    except ValueError as e:
        return {"error": f"Failed to parse date: {str(e)}"}
