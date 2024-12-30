"""ThermoWorks Cloud client library.

This module provides the primary interface for interacting with the ThermoWorks Cloud
service, allowing users to access their ThermoWorks Cloud devices and data.

This is the main public module of the thermoworks_cloud package.
"""

from .auth import Auth, AuthFactory, AuthenticationError, AuthenticationErrorReason
from .core import ThermoworksCloud
from . import models

# The publicly accessible classes for this module
__all__ = ["ThermoworksCloud", "Auth", "AuthFactory",
           "AuthenticationError", "AuthenticationErrorReason", "models"]

# Tells pdoc how to parse the doc strings in this module
__docformat__ = "google"
