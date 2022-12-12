"""Identity assertions"""
from c8y_api.model import ManagedObject

from c8y_test_core.assert_device import AssertDevice


class DeviceNotFound(AssertionError):
    """Device not found"""


class AssertIdentity(AssertDevice):
    """Identity assertions"""

    # pylint: disable=too-few-public-methods
    def assert_exists(
        self,
        external_id: str,
        external_type: str = "c8y_Serial",
        **kwargs,
    ) -> ManagedObject:
        """Assert that the external id exists"""
        try:
            mo = self.context.client.identity.get_object(
                external_id=external_id, external_type=external_type
            )
        except KeyError as ex:
            raise DeviceNotFound() from ex

        assert mo.id
        return mo
