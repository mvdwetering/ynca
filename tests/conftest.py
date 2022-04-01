"""Fixtures for testing."""
from typing import Callable
from unittest import mock

import pytest

from .mock_yncaconnection import YncaConnectionMock


@pytest.fixture
def connection():
    c = YncaConnectionMock()
    c.setup_responses()
    return c


@pytest.fixture
def update_callback() -> Callable[[], None]:
    return mock.MagicMock()
