"""Device configuration assertions"""
from c8y_api.model import Operation
from c8y_test_core.assert_device import AssertDevice
from c8y_test_core.assert_binaries import Binaries
from c8y_test_core.models import Configuration
from c8y_test_core.assert_operation import AssertOperation
from c8y_test_core.utils import RandomNameGenerator


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
        contents: str = None,
        file: str = None,
        **kwargs,
    ) -> Operation:
        """Apply a configuration given a given contents or file and wait for the operation to complete.

        This method is a convinience function to make it easier and quicker to apply configuration to a device.

        If the configuration does not contain a url, then a temporary file will be uploaded to Cumulocity and
        the url will be included in the configuration operation sent to the device.

        Args:
            configuration (str, optiona)
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
            tempname = "tempfile-" + RandomNameGenerator.random_name()
            with Binaries(self.context).new_binary(
                name=tempname, file=file, contents=contents
            ) as ref:
                configuration.url = ref.url
                operation = self.set_configuration(configuration, **kwargs)
                operation.assert_success()
                return operation

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
            "c8y_UploadConfigFile": configuration.__dict__,
            **kwargs,
        }
        return self._execute(**fragments)
