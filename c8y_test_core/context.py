"""Context"""
from dataclasses import dataclass
from typing import Optional
import logging
from c8y_api import CumulocityApi


@dataclass
class AssertContext:
    """Assertion context"""

    device_id: str
    client: CumulocityApi
    log: Optional[logging.Logger] = None

    def domain(self) -> str:
        """Get the Cumulocity domain without the scheme"""
        assert self.client, "client is empty"
        url = self.client.base_url.rstrip("/")
        if "://" in url:
            return url.split("://")[1]
        return url
