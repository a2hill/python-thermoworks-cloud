"""ThermoWorks Cloud client library.

This module provides the primary interface for interacting with the ThermoWorks Cloud
service, allowing users to access their ThermoWorks Cloud devices and data.

This is the main public module of the thermoworks_cloud package.
"""

import logging

from . import models
from .auth import Auth, AuthenticationError, AuthenticationErrorReason, AuthFactory
from .core import ThermoworksCloud, ResourceNotFoundError

# The publicly accessible classes for this module
__all__ = [
    "ThermoworksCloud",
    "Auth",
    "AuthFactory",
    "AuthenticationError",
    "AuthenticationErrorReason",
    "ResourceNotFoundError",
    "models",
]

# Tells pdoc how to parse the doc strings in this module
__docformat__ = "google"

# Allows for consuming applications to look at log messages if they'd like
_LOGGER = logging.getLogger(__name__)
_LOGGER.addHandler(logging.NullHandler())
