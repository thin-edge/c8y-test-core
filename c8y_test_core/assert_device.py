"""Device assertion"""
from c8y_api.model import Operation

from c8y_test_core.assert_operation import AssertOperation
from c8y_test_core.context import AssertContext


class AssertDevice:
    """Assertions"""

    # pylint: disable=too-few-public-methods
    def __init__(self, context: AssertContext) -> None:
        self.context = context

    def _execute(self, **kwargs) -> AssertOperation:
        device_id = kwargs.pop("device_id", self.context.device_id)
        operation = Operation(self.context.client, device_id, **kwargs).create()
        return AssertOperation(self.context, operation)
