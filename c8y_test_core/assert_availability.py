"""Device availability and connection assertions"""
from c8y_api.model import ManagedObject
from c8y_test_core.assert_device import AssertDevice


class AssertDeviceAvailability(AssertDevice):
    """Device availability and connection assertions"""

    class ConnectionStatus:
        """Connection status"""

        # pylint: disable=too-few-public-methods
        CONNECTED = "CONNECTED"
        DISCONNECTED = "DISCONNECTED"

    class AvailabilityStatus:
        """Availability status"""

        # pylint: disable=too-few-public-methods
        AVAILABLE = "AVAILABLE"
        UNAVAILABLE = "UNAVAILABLE"
        MAINTENANCE = "MAINTENANCE"

    def assert_device_available(
        self,
        mo: ManagedObject = None,
        **kwargs,
    ) -> ManagedObject:
        """Assert that the device availability status (c8y_Availability.status)
        is set to AVAILABLE
        """
        if mo is None:
            mo = self.context.client.inventory.get(self.context.device_id)
        assert (
            mo.to_json()["c8y_Availability"]["status"]
            == self.AvailabilityStatus.AVAILABLE
        )
        return mo

    def assert_device_unavailable(
        self,
        mo: ManagedObject = None,
        **kwargs,
    ) -> ManagedObject:
        """Assert that the device availability status (c8y_Availability.status)
        is set to UNAVAILABLE
        """
        if mo is None:
            mo = self.context.client.inventory.get(self.context.device_id)
        assert (
            mo.to_json()["c8y_Availability"]["status"]
            == self.AvailabilityStatus.UNAVAILABLE
        )
        return mo

    def assert_device_maintenance(
        self,
        mo: ManagedObject = None,
        **kwargs,
    ) -> ManagedObject:
        """Assert that the device availability status (c8y_Availability.status)
        is set to MAINTENANCE
        """
        if mo is None:
            mo = self.context.client.inventory.get(self.context.device_id)
        assert (
            mo.to_json()["c8y_Availability"]["status"]
            == self.AvailabilityStatus.MAINTENANCE
        )
        return mo

    def assert_device_connected(
        self,
        mo: ManagedObject = None,
        **kwargs,
    ) -> ManagedObject:
        """Assert that the device connection status (c8y_Availability.status)
        is set to CONNECTED
        """
        if mo is None:
            mo = self.context.client.inventory.get(self.context.device_id)
        assert (
            mo.to_json()["c8y_Connection"]["status"] == self.ConnectionStatus.CONNECTED
        )
        return mo

    def assert_device_disconnected(
        self,
        mo: ManagedObject = None,
        **kwargs,
    ) -> ManagedObject:
        """Assert that the device connection status (c8y_Connection.status)
        is set to DISCONNECTED
        """
        if mo is None:
            mo = self.context.client.inventory.get(self.context.device_id)
        assert (
            mo.to_json()["c8y_Connection"]["status"]
            == self.ConnectionStatus.DISCONNECTED
        )
        return mo

    def create_operation(self, **kwargs):
        """Create an operation"""
        fragments = {
            "description": "Send operation",
            **kwargs,
        }
        return self._execute(**fragments)
