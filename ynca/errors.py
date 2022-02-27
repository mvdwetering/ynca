"""Ynca errors."""


class YncaException(Exception):
    """Base error for ynca."""


class YncaConnectionError(YncaException):
    """Connection to the device failed"""


class YncaInitializationFailedException(YncaException):
    """Initialization of Zone failed"""
