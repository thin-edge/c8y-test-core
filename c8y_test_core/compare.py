"""Comparison helpers"""
import re


class RegexPattern:
    """Assert that a given string meets some expectations."""

    def __init__(self, pattern, flags=0):
        self._regex = re.compile(pattern, flags)

    def __eq__(self, actual):
        return bool(self._regex.match(actual))

    def __repr__(self):
        return self._regex.pattern


def compare_dataclass(obj1: object, obj2: object) -> bool:
    """Compare objects"""
    obj1_dict = obj1.__dict__ if not hasattr(obj1, "items") else obj1
    obj2_dict = obj2.__dict__ if not hasattr(obj2, "items") else obj2

    for key, value in obj2_dict.items():  # type: ignore
        if not value:
            continue

        if key not in obj1_dict:  # type: ignore
            return False

        if isinstance(value, re.Pattern):
            if not re.match(value, obj1_dict.get(key, "")):  # type: ignore
                return False
        elif isinstance(value, dict):
            return compare_dataclass(obj1_dict.get(key, ""), value)  # type: ignore
        else:
            if value != obj1_dict.get(key, ""):  # type: ignore
                return False

    return True
