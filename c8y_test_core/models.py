"""Models"""
import dataclasses
from typing import Dict

from c8y_test_core.compare import compare_dataclass


@dataclasses.dataclass
class Firmware:
    """Firmware"""

    name: str = ""
    version: str = ""
    url: str = ""

    def __eq__(self, obj: object) -> bool:
        if isinstance(obj, Firmware):
            return compare_dataclass(self, obj)
        if isinstance(obj, dict):
            return compare_dataclass(self, Firmware(**obj))
        return False


@dataclasses.dataclass
class Software:
    """Software"""

    name: str = ""
    version: str = ""
    url: str = ""
    action: str = ""
    softwareType: str = ""

    def __eq__(self, obj: object) -> bool:
        if isinstance(obj, Software):
            return compare_dataclass(self, obj)
        if isinstance(obj, dict):
            return compare_dataclass(self, Software(**obj))
        return False

    def to_dict(self) -> Dict[str, str]:
        """Return software item as a dictionary"""
        return self.__dict__


@dataclasses.dataclass
class Configuration:
    """Configuration"""

    type: str = ""
    url: str = ""

    def __eq__(self, obj: object) -> bool:
        return compare_dataclass(self, obj)
