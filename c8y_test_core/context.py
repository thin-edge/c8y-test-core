"""Context"""
from dataclasses import dataclass
import logging
from c8y_api import CumulocityApi


@dataclass
class AssertContext:
    """Assertion context"""

    device_id: str = ""
    client: CumulocityApi = None
    log: logging.Logger = None
