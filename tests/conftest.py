"""Fixtures for testing."""

from collections.abc import Callable
from unittest import mock

import pytest

from .mock_yncaconnection import YncaConnectionMock


@pytest.fixture
def connection() -> YncaConnectionMock:
    c = YncaConnectionMock()
    c.setup_responses()
    return c


@pytest.fixture
def update_callback() -> Callable[[str, str], None]:
    return mock.MagicMock()
