"""Test fixtures
"""
from unittest.mock import Mock
from c8y_test_core.context import AssertContext
from c8y_test_core.c8y import CumulocityApi


def create_context(device_id: str = "unittest001") -> AssertContext:
    client = Mock(CumulocityApi)
    return AssertContext(device_id=device_id, client=client)
