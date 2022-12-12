"""Models"""
import dataclasses

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
        return compare_dataclass(self, Firmware(**obj))


@dataclasses.dataclass
class Software:
    """Software"""

    name: str = ""
    version: str = ""
    url: str = ""
    action: str = ""

    def __eq__(self, obj: object) -> bool:
        if isinstance(obj, Software):
            return compare_dataclass(self, obj)
        return compare_dataclass(self, Software(**obj))


@dataclasses.dataclass
class Configuration:
    """Configuration"""

    type: str = ""
    url: str = ""

    def __eq__(self, obj: object) -> bool:
        return compare_dataclass(self, obj)
