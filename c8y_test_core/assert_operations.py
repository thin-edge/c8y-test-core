"""Operation collection assertions"""
from typing import Any, List, Optional

from c8y_test_core.context import AssertContext
from c8y_test_core.retry import configure_retry_on_members, strip_retry_parameters


class AssertOperations:
    """Operations assertions"""

    def __init__(self, context: AssertContext, **kwargs):
        self.context = context
        configure_retry_on_members(self, "^assert_.+", **kwargs)

    def assert_count(
        self,
        min_count: Optional[int] = 1,
        max_count: Optional[int] = None,
        *,
        fragment: Optional[str] = None,
        status: Optional[str] = None,
        device_id: Optional[str] = None,
        **kwargs,
    ) -> List[Any]:
        """Assert the count of operations given a given status"""

        # set existing device id context if not explicitly set
        if device_id is None:
            device_id = self.context.device_id

        params = {
            "limit": 1000,
            "page_size": 1000,
            **strip_retry_parameters(kwargs),
        }

        if device_id:
            params["device_id"] = device_id

        if fragment:
            params["fragment"] = fragment

        if status:
            params["status"] = status

        operations = self.context.client.operations.get_all(**params)
        total = len(operations)

        if min_count is not None and (max_count is not None):
            assert min_count <= total <= max_count, (
                "Operation count is not between min and max range (inclusive)\n"
                f"want=Between {min_count} and {max_count}\n"
                f"got={total}"
            )

        if min_count is not None and max_count is None:
            assert total >= min_count, (
                "Operation count is less than expected\n"
                f"want= >= {min_count}\n"
                f"got={total}"
            )

        if min_count is None and max_count is not None:
            assert total <= max_count, (
                "Operation count is greater than expected\n"
                f"want= <= {max_count}\n"
                f"got={total}"
            )

        return operations

    def assert_all_completed(
        self, device_id: Optional[str] = None, **kwargs
    ) -> List[Any]:
        """Assert that all operations have been completed, e.g. no operations are in
        PENDING or EXECUTING status.

        Operations that are still in PENDING or EXECUTING status, usually indicate that there
        is a problem with the agent, so it is good practice to run this assertion when testing
        Cumulocity IoT agents.
        """
        kwargs.pop("status", None)
        self.assert_count(
            min_count=0, max_count=0, device_id=device_id, status="PENDING", **kwargs
        )
        return self.assert_count(
            min_count=0, max_count=0, device_id=device_id, status="EXECUTING", **kwargs
        )
