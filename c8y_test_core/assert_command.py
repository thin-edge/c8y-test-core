"""Command assertions"""
from c8y_test_core.assert_device import AssertDevice
from c8y_test_core.assert_operation import AssertOperation


class Command(AssertDevice):
    """Command assertions"""

    # pylint: disable=too-few-public-methods
    def execute(self, text: str, **kwargs) -> AssertOperation:
        """Execute a shell command via an operation"""
        fragments = {
            "description": "Execute shell command",
            "c8y_Command": {
                "text": text,
            },
            **kwargs,
        }
        return self._execute(**fragments)
