"""Ynca errors."""


class YncaException(Exception):
    """Base error for ynca."""


class YncaConnectionError(YncaException):
    """Error connecting to the device, no connection could be setup. Most likely wrong connection info provided or device powered Off."""


class YncaConnectionFailed(YncaException):
    """Connection made, but broke. Most likely connecting to a device that already has the YNCA port occupied."""


class YncaInitializationFailedException(YncaException):
    """Initialization of Zone failed.
Several possible causes, for example:
* connecting to a device that already has the YNCA port occupied
* bug in the ynca component > enable debug logging for more info"""
