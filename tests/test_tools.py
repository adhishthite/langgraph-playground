"""Tests for tools functionality."""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from app.tools.date_tool import get_current_date, parse_date


def test_get_current_date():
    """Test the get_current_date tool."""
    result = get_current_date.func("")  # Call the underlying function directly with empty string input
    assert isinstance(result, str)
    # Verify the result is a valid ISO format date
    datetime.fromisoformat(result)  # Should not raise an exception


def test_parse_date_valid():
    """Test the parse_date tool with valid input."""
    test_date = "2023-04-25T10:30:15"
    result = parse_date.func(test_date)  # Call the underlying function directly

    assert result["year"] == 2023
    assert result["month"] == 4
    assert result["day"] == 25
    assert result["hour"] == 10
    assert result["minute"] == 30
    assert result["second"] == 15


def test_parse_date_invalid():
    """Test the parse_date tool with invalid input."""
    test_date = "not-a-date"
    result = parse_date.func(test_date)  # Call the underlying function directly

    assert "error" in result
    assert "Failed to parse date" in result["error"]
