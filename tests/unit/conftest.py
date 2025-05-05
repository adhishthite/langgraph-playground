"""Configurations for unit tests."""

import pytest


def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")


def pytest_collection_modifyitems(items):
    """Modify test items to add markers."""
    for item in items:
        item.add_marker(pytest.mark.unit)
