"""json reader"""
import json
import subprocess
from typing import Any, Callable, List, Optional


class JsonReader:
    """JSON reader supports parsing stdout and returning a list
    using the preferred class factory, or by default a list of dictionaries
    """

    def __init__(self, proc: subprocess.Popen) -> None:
        self._proc = proc

    def wait(self, timeout: Optional[float] = None):
        """Wait for the process to finish

        Args:
            timeout (float, optional): Timeout in seconds. Defaults to None.
        """
        code = self._proc.wait(timeout)
        assert code == 0

    def read_all(self, func: Optional[Callable] = None) -> Optional[List[Any]]:
        """Read all data and transform the output using a given function

        Args:
            func (Optional[Callable], optional): Function to be called on each outupt line.
                Defaults to None.

        Returns:
            Optional[List[Any]]: List of objects created from each line of output
        """
        if not self._proc.stdout:
            return []

        if func:
            return [func(json.loads(line)) for line in self._proc.stdout]
        return [json.loads(line) for line in self._proc.stdout]
