"""Device configuration assertions"""
from typing import List, Optional
from c8y_api.model import Operation, ManagedObject
from c8y_test_core.assert_device import AssertDevice
from c8y_test_core.assert_binaries import Binaries
from c8y_test_core.models import Configuration
from c8y_test_core.assert_operation import AssertOperation
from c8y_test_core.utils import RandomNameGenerator


SUPPORTED_CONFIGURATIONS = "c8y_SupportedConfigurations"


class DeviceConfiguration(AssertDevice):
    """Device configuration assertions"""

    def set_configuration(
        self, configuration: Configuration, **kwargs
    ) -> AssertOperation:
        """Create a configuration operation c8y_DownloadConfigFile
        This should trigger the device/agent to download the configuration from the provided url
        """
        config_type = configuration.__dict__.get("type", "")
        fragments = {
            "description": f"Send configuration snapshot {config_type} to device",
            "c8y_DownloadConfigFile": configuration.__dict__,
            **kwargs,
        }
        return self._execute(**fragments)

    def apply_and_wait(
        self,
        configuration: Configuration,
        contents: Optional[str] = None,
        file: Optional[str] = None,
        **kwargs,
    ) -> Operation:
        """Apply a configuration given a given contents or file and wait for the operation to complete.

        This method is a convenience function to make it easier and quicker to apply configuration to a device.

        If the configuration does not contain a url, then a temporary file will be uploaded to Cumulocity and
        the url will be included in the configuration operation sent to the device.

        Args:
            configuration (str)
            contents (str, optional): Contents to be sent to the device. Ignored if set to None.
            file (str, optional): Path to the file to be applied to the device. Ignored if set to None.

        Returns:
            Operation: Successful operation
        """
        # Use url provided by the user
        if configuration.url:
            operation = self.set_configuration(configuration, **kwargs)
            return operation.assert_success()

        # Create temporary file to upload to Cumulocity
        if file is not None or contents is not None:
            temp_name = "tempfile-" + RandomNameGenerator.random_name()
            with Binaries(self.context).new_binary(
                name=temp_name, file=file, contents=contents
            ) as ref:
                configuration.url = ref.url
                operation = self.set_configuration(configuration, **kwargs)
                return operation.assert_success()

        raise ValueError("User must provide either file or contents")

    def get_configuration(
        self, configuration: Configuration, **kwargs
    ) -> AssertOperation:
        """Create a configuration operation (c8y_UploadConfigFile) to get the configuration
        from a device.

        This should trigger the device/agent to uploaded the configuration type to the platform
        """
        config_type = configuration.__dict__.get("type", "")
        fragments = {
            "description": f"Retrieve {config_type} configuration snapshot from device",
            "c8y_UploadConfigFile": {
                "type": config_type,
            },
            **kwargs,
        }
        return self._execute(**fragments)

    def assert_supported_types(
        self,
        *types: str,
        includes: bool = False,
        mo: Optional[ManagedObject] = None,
        **kwargs,
    ) -> ManagedObject:
        """Assert that the managed object has supported configuration
        in the 'c8y_SupportedConfigurations' fragment.

        Args:
            *types (*str): List of expected configuration types
            includes (boolean, optional): Only check if the list includes the given types. It only
                checks if the given types are there and does not care about additional types.
                Defaults to False

            mo (ManagedObject, optional): Managed object to use in comparison. Defaults to the current
                context.

        Returns:
            ManagedObject: Managed object
        """
        if mo is None:
            mo = self.context.client.inventory.get(self.context.device_id)

        mo_json = mo.to_json()
        assert (
            SUPPORTED_CONFIGURATIONS in mo_json
        ), f"Supported configuration fragment is missing {SUPPORTED_CONFIGURATIONS} from managed object"
        supported_configs = mo_json.get(SUPPORTED_CONFIGURATIONS, [])

        if includes:
            missing = [
                typename for typename in types if typename not in supported_configs
            ]
            assert not missing, (
                f"Supported Configuration fragment ({SUPPORTED_CONFIGURATIONS}) is missing some types."
                f"\nmissing: {missing}"
                f"\ngot: {supported_configs}"
            )
        else:
            assert sorted(supported_configs) == sorted(types), (
                f"Supported Configuration fragment ({SUPPORTED_CONFIGURATIONS}) does not match."
                f"\nwanted: {sorted(types)}"
                f"\ngot:    {sorted(supported_configs)}"
            )

        return mo
