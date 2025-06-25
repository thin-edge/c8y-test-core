"""Device Profile management"""
from typing import Dict, Any, Optional, List

from c8y_api.model import ManagedObject, Operation

from c8y_test_core.assert_device import AssertDevice
from c8y_test_core.assert_operation import AssertOperation
from c8y_test_core.models import Software, Configuration, Firmware


class DeviceProfile(AssertDevice):
    """Device Profile management"""

    def create(
        self,
        name: str,
        firmware: Optional[Firmware] = None,
        software: Optional[List[Software]] = None,
        config: Optional[List[Configuration]] = None,
        profile: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> ManagedObject:
        """Create a new device profile in the Cumulocity IoT Device Profile repository

        Args:
            name (str): Name of the device profile
            profile (Dict[str, Any], optional): Device profile contents as a dictionary. Use if you want
                finer control over the c8y_DeviceProfile fragment value. Defaults to None

            firmware (Firmware, optional): Firmware to include
            software (List[Software], optional): List of software to include
            config (List[Configuration], optional): List of configuration to include

        Returns:
            ManagedObject: The created device profile operation object
        """

        contents = {
            "software": [],
            "configuration": [],
            **(profile or {}),
        }

        if firmware:
            contents["firmware"] = firmware

        if software:
            contents["software"] = [item.__dict__ for item in software]

        if config:
            contents["configuration"] = [item.__dict__ for item in config]

        fragments = {
            "c8y_Filter": {},
            "c8y_DeviceProfile": contents,
        }

        mo = ManagedObject(
            self.context.client, type="c8y_Profile", name=name, **fragments
        ).create()
        return mo

    def apply(
        self, profile_id: str, device_id: Optional[str], **kwargs
    ) -> AssertOperation:
        """Apply a device profile to a device"""

        if not device_id:
            device_id = self.context.device_id

        assert device_id, "device id must not be empty"

        # Get the profile details from the given managed object
        profile = self.context.client.inventory.get(profile_id).to_full_json()

        fragments = {
            "profileId": profile_id,
            "profileName": profile["name"],
            "c8y_DeviceProfile": profile["c8y_DeviceProfile"],
        }

        operation = Operation(
            self.context.client,
            device_id,
            description=f"Assign device profile {profile['name']} to device",
            **fragments,
        ).create()
        return AssertOperation(self.context, operation, **kwargs)

    def delete(self, profile_id: str, **kwargs):
        """Delete a device profile managed object

        Arguments:
            profile_id (str): Device profile managed object id
        """
        self.context.client.inventory.delete(profile_id)

    def assert_installed(
        self, profile_id: str, mo: Optional[ManagedObject] = None, **kwargs
    ) -> ManagedObject:
        """Assert that a given device profile is installed on a device
        by checking the c8y_Profile fragment

        Returns:
            ManagedObject: Managed object
        """
        if mo is None:
            mo = self.context.client.inventory.get(self.context.device_id)
        mo_data = mo.to_full_json()

        profile = self.context.client.inventory.get(profile_id).to_full_json()

        assert (
            "c8y_Profile" in mo_data
        ), "Managed object does not have a c8y_Profile fragment"

        assert mo_data["c8y_Profile"]["profileId"] == profile_id
        assert mo_data["c8y_Profile"]["profileName"] == profile["name"]
        assert mo_data["c8y_Profile"]["profileExecuted"]
        return mo

    def assert_not_installed(
        self, profile_id: str, mo: Optional[ManagedObject] = None, **kwargs
    ) -> ManagedObject:
        """Assert that a given device profile is not currently installed on a device

        Returns:
            ManagedObject: Managed object
        """
        if mo is None:
            mo = self.context.client.inventory.get(self.context.device_id)
        mo_data = mo.to_full_json()

        if "c8y_Profile" not in mo_data:
            return mo

        profile = self.context.client.inventory.get(profile_id).to_full_json()
        assert mo_data["c8y_Profile"]["profileId"] != profile_id
        assert mo_data["c8y_Profile"]["profileName"] != profile["name"]
        return mo
