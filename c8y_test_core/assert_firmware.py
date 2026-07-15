"""Firmware management
"""
from typing import Optional
from c8y_api.model import ManagedObject

from c8y_test_core.assert_device import AssertDevice
from c8y_test_core.assert_inventory import AssertInventory
from c8y_test_core.assert_operation import AssertOperation
from c8y_test_core.compare import compare_dataclass
from c8y_test_core.models import Firmware


class FirmwareManagement(AssertDevice):
    """Firmware management assertions"""

    def install(self, firmware: Firmware, **kwargs) -> AssertOperation:
        """Install firmware via the c8y_Firmware operation"""
        fragments = {
            "description": f"Install firmware: {firmware.name}={firmware.version}",
            "c8y_Firmware": firmware.__dict__,
            **kwargs,
        }
        return self._execute(**fragments)

    def assert_firmware(
        self, expected_firmware: Firmware, mo: Optional[ManagedObject] = None, **kwargs
    ) -> ManagedObject:
        """Assert a firmware name and optional version"""
        if mo is None:
            mo = self.context.client.inventory.get(self.context.device_id)

        mo = AssertInventory(self.context).assert_contains_fragments(fragments=["c8y_Firmware"], mo=mo)

        actual_firmware = mo.to_json().get("c8y_Firmware", {})
        assert compare_dataclass(actual_firmware, expected_firmware), (
            f"Firmware does not match. "
            f"wanted={expected_firmware}, got={actual_firmware}"
        )
        return mo

    def assert_not_firmware(
        self, expected_firmware: Firmware, mo: Optional[ManagedObject] = None, **kwargs
    ):
        """Assert that the device firmware does not match"""
        if mo is None:
            mo = self.context.client.inventory.get(self.context.device_id)

        mo = AssertInventory(self.context).assert_contains_fragments(fragments=["c8y_Firmware"], mo=mo)
        actual_firmware = mo.to_json().get("c8y_Firmware", {})

        assert not compare_dataclass(
            actual_firmware, expected_firmware
        ), f"Firmware is installed. wanted={expected_firmware}, got={actual_firmware}"
        return mo
