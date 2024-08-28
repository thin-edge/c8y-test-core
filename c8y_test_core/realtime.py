"""c8y realtime utilities
The functions here rely on the cli tool go-c8y-cli!
"""
import subprocess
from c8y_test_core.proc_utils import JsonReader


class Subscriber:
    """Subscriber factory"""

    @classmethod
    def _subscribe(cls, typename: str, device_id: str, duration: int) -> JsonReader:
        # pylint: disable=consider-using-with
        proc = subprocess.Popen(
            [
                "c8y",
                "measurements",
                "subscribe",
                "--device",
                device_id,
                "--duration",
                f"{duration}s",
            ],
            universal_newlines=True,
            stdout=subprocess.PIPE,
        )
        return JsonReader(proc)

    # pylint: disable=too-few-public-methods
    @classmethod
    def to_measurements(cls, device_id: str, duration: int) -> JsonReader:
        """Create a subscription to measurements for a device

        Args:
            device_id (str): device id to subscribe to
            duration (int): Duration in seconds to subscribe for

        Returns:
            JsonReader: Reader which can be called to access the data
        """
        return cls._subscribe("measurements", device_id, duration)

    @classmethod
    def to_events(cls, device_id: str, duration: int) -> JsonReader:
        """Create a subscription to events for a device

        Args:
            device_id (str): device id to subscribe to
            duration (int): Duration in seconds to subscribe for

        Returns:
            JsonReader: Reader which can be called to access the data
        """
        # pylint: disable=consider-using-with
        return cls._subscribe("events", device_id, duration)

    @classmethod
    def to_alarms(cls, device_id: str, duration: int) -> JsonReader:
        """Create a subscription to alarms for a device

        Args:
            device_id (str): device id to subscribe to
            duration (int): Duration in seconds to subscribe for

        Returns:
            JsonReader: Reader which can be called to access the data
        """
        # pylint: disable=consider-using-with
        return cls._subscribe("alarms", device_id, duration)

    @classmethod
    def to_operations(cls, device_id: str, duration: int) -> JsonReader:
        """Create a subscription to operations for a device

        Args:
            device_id (str): device id to subscribe to
            duration (int): Duration in seconds to subscribe for

        Returns:
            JsonReader: Reader which can be called to access the data
        """
        # pylint: disable=consider-using-with
        return cls._subscribe("operations", device_id, duration)

    @classmethod
    def to_inventory(cls, device_id: str, duration: int) -> JsonReader:
        """Create a subscription to managed objects/inventory for a device

        Args:
            device_id (str): device id to subscribe to
            duration (int): Duration in seconds to subscribe for

        Returns:
            JsonReader: Reader which can be called to access the data
        """
        # pylint: disable=consider-using-with
        return cls._subscribe("inventory", device_id, duration)
