"""Operation assertions"""
import json
from typing import Any, Dict
from c8y_api.model import Operation

from c8y_test_core.context import AssertContext
from c8y_test_core.retry import configure_retry_on_members

from .errors import FinalAssertionError
from . import compare


class AssertOperation:
    """Operation assertions"""

    def __init__(self, context: AssertContext, operation: Operation, **kwargs):
        self.context = context
        self.operation = operation
        configure_retry_on_members(self, "^assert_.+", **kwargs)

    def __repr__(self) -> str:
        return json.dumps(self.to_json())

    def to_json(self) -> Dict[str, Any]:
        """Get operation as dictionary"""
        return self.operation.to_json()

    def fetch_operation(self):
        """Refresh the operation by fetching it again from the platform"""
        self.operation = self.context.client.operations.get(self.operation.id)
        return self

    def assert_success(self, **kwargs) -> Operation:
        """Assert that the operation status to be set to SUCCESS"""
        self.fetch_operation()

        try:
            assert self.operation.status == Operation.Status.SUCCESSFUL, (
                f"Expected operation (id={self.operation.id}) to be {Operation.Status.SUCCESSFUL}, "
                f"but got: {self.operation.status} "
                f"(failureReason: {self.operation.to_json().get('failureReason', '')})"
            )
        except AssertionError as ex:
            if self.operation.status == Operation.Status.FAILED:
                raise FinalAssertionError(ex)
            raise

        return self.operation

    def assert_pending(self, **kwargs) -> Operation:
        """Assert that the operation status to be set to PENDING"""
        self.fetch_operation()
        assert self.operation.status == Operation.Status.PENDING, (
            f"Expected operation (id={self.operation.id}) to be {Operation.Status.PENDING}, "
            f"but got: {self.operation.status}"
        )
        return self.operation

    def assert_failed(self, failure_reason: str = ".+", **kwargs) -> Operation:
        """Assert that the operation status to be set to FAILED

        Args:
            failure_reason (str, optional): Assert a failure reason using a regex pattern.
                If set to None, then it is skipped. Defaults to ".+".

        Returns:
            Operation: Current operation
        """
        self.fetch_operation()
        try:
            assert self.operation.status == Operation.Status.FAILED, (
                f"Expected operation (id={self.operation.id}) to be {Operation.Status.FAILED}, "
                f"but got: {self.operation.status}"
            )
        except AssertionError as ex:
            if self.operation.status == Operation.Status.SUCCESSFUL:
                raise FinalAssertionError(ex)
            raise

        if failure_reason is not None:
            assert (
                "failureReason" in self.operation
            ), "failureReason is mandatory when setting to FAILED"
            actual_failure_reason = self.operation.to_json().get("failureReason")
            assert actual_failure_reason == compare.RegexPattern(failure_reason), (
                "Failure reason does not match regex pattern\n"
                f"got: {actual_failure_reason}\n"
                f"wanted: {failure_reason}"
            )
        return self.operation

    def assert_done(self, **kwargs) -> Operation:
        """Assert that the operation status is either SUCCESS or FAILED"""
        self.fetch_operation()
        assert self.operation.status in (
            Operation.Status.SUCCESSFUL,
            Operation.Status.FAILED,
        ), (
            f"Expected operation (id={self.operation.id}) to be done, "
            f"but got: {self.operation.status}"
        )
        return self.operation

    def assert_not_done(self, **kwargs) -> Operation:
        """Assert that the operation status to be not done (e.g. SUCCESSFUL or FAILED)"""
        self.fetch_operation()
        assert self.operation.status not in [
            Operation.Status.SUCCESSFUL,
            Operation.Status.FAILED,
        ](
            f"Expected operation (id={self.operation.id}) to not be done "
            f"[{Operation.Status.SUCCESSFUL} or {Operation.Status.FAILED}]), "
            f"but got: {self.operation.status}"
        )
        return self.operation

    def assert_not_pending(self, **kwargs) -> Operation:
        """Assert that the operation status to be not PENDING"""
        self.fetch_operation()
        assert self.operation.status != Operation.Status.PENDING, (
            f"Expected operation (id={self.operation.id}) to not be {Operation.Status.PENDING}, "
            f"but got: {self.operation.status}"
        )
        return self.operation

    def assert_delivered(self, **kwargs) -> Operation:
        """Assert that the operation was delivered (only supported if the agent
        is communicating via MQTT.
        """
        self.fetch_operation()

        props = self.operation.to_json()

        assert (
            "delivery" in props
        ), f"Expected operation (id={self.operation.id}) to contain the delivery fragment"

        delivery_status = props["delivery"].get("status", "")
        assert delivery_status == "DELIVERED", (
            f"Expected operation (id={self.operation.id}) to be DELIVERED, "
            f"but got: {delivery_status}"
        )
        return self.operation

    def assert_executing(self, **kwargs) -> Operation:
        """Assert that the operation is executing"""
        self.fetch_operation()
        assert self.operation.status == Operation.Status.EXECUTING, (
            f"Expected operation (id={self.operation.id}) to be EXECUTING, "
            f"but got: {self.operation.status}"
        )
        return self.operation

    def create(self, device_id: str, **kwargs):
        """Create an operation"""
        return AssertOperation(
            context=self.context,
            operation=Operation(
                c8y=self.context.client, device_id=device_id, **kwargs
            ).create(),
        )
