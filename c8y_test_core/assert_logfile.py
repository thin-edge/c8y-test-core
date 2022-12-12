"""Device logfile assertions"""
from datetime import datetime, timedelta
from c8y_test_core.assert_device import AssertDevice
from c8y_test_core.assert_operation import AssertOperation


class DeviceLogFile(AssertDevice):
    """Device log file assertions"""

    def get_logfile(
        self,
        type: str,
        date_from: datetime,
        date_to: datetime,
        maximum_lines: int = 100,
        search_text: str = "",
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
