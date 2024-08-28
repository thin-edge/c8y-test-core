"""Device logfile assertions"""
from datetime import datetime, timedelta
from typing import Optional
from c8y_api.model import ManagedObject
from c8y_test_core.assert_device import AssertDevice
from c8y_test_core.assert_operation import AssertOperation

SUPPORTED_LOGFILE_TYPES = "c8y_SupportedLogs"


class DeviceLogFile(AssertDevice):
    """Device log file assertions"""

    def assert_supported_types(
        self, *types: str, include: Optional[bool] = True, mo: Optional[ManagedObject] = None, **kwargs
    ) -> ManagedObject:
        """Assert presence of some supported log file types by checking the c8y_SupportedLogs
        fragment of the inventory managed object.

        It will only check if the given supported log file types exist, other supported log file
        types are allowed to also exist which are not included in the assertion.

        Args:
            *types (str): List of expected supported operations
            include (bool): Only check if the given types are included
                and don't fail if additional types are found

        Returns:
            ManagedObject: Managed object
        """
        if mo is None:
            mo = self.context.client.inventory.get(self.context.device_id)
        mo_json = mo.to_json()

        assert (
            SUPPORTED_LOGFILE_TYPES in mo_json
        ), f"Supported log file types fragment is missing {SUPPORTED_LOGFILE_TYPES} from managed object"
        supported_types = mo_json.get(SUPPORTED_LOGFILE_TYPES, [])

        if include:
            # Only check if the given types are present and ignore extra ones
            missing = [
                typeName for typeName in types if typeName not in supported_types
            ]
            assert len(missing) == 0, (
                "c8y_SupportedLogs is missing expected types.\n"
                f"missing={missing}\n"
                f"got={supported_types}"
            )
        else:
            # Exact match, check all types
            expected_types = sorted(types)
            actual_types = sorted(supported_types)
            assert actual_types == expected_types, (
                "c8y_SupportedLogs does not match expected list.\n"
                f"want={expected_types}\n"
                f"got={actual_types}"
            )

        return mo

    def get_logfile(
        self,
        type: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        maximum_lines: Optional[int] = 100,
        search_text: Optional[str] = "",
        **kwargs,
    ) -> AssertOperation:
        """Create a log file request operation c8y_LogfileRequest

        Args:
            type (str): Log file type
            date_from (datetime, optional): Only include log entries from a specific date. Defaults to now - 1 day
            date_to (datetime, optional): Only include log entries to a specific date. Defaults to now
            maximum_lines (int, optional): Maximum number of log entries
            search_text (str, optional): Only include log entries matching a specific pattern. Defaults to ""

        Returns:
            AssertOperation: Operation assertion
        """

        if date_from is None:
            date_from = datetime.now() - timedelta(days=1)

        if date_to is None:
            date_to = datetime.now()

        fragments = {
            "description": f"Request log file type {type} from device",
            "c8y_LogfileRequest": {
                "dateFrom": date_from.isoformat() + "Z",
                "dateTo": date_to.isoformat() + "Z",
                "logFile": type,
                "maximumLines": maximum_lines,
                "searchText": search_text,
            },
            **kwargs,
        }

        return self._execute(**fragments)
