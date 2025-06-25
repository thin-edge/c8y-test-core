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

    def domain(self) -> str:
        """Get the Cumulocity domain without the scheme"""
        url = self.client.base_url.rstrip("/")
        if "://" in url:
            return url.split("://")[1]
        return url
