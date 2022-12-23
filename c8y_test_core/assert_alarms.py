"""Alarm assertions"""
import re
from typing import List

from c8y_api.model import Alarm

from c8y_test_core.assert_device import AssertDevice


class AlarmNotFound(AssertionError):
    """Alarm not found"""


class Alarms(AssertDevice):
    """Alarm assertions"""

    # pylint: disable=too-few-public-methods

    def assert_count(
        self,
        expected_text: str = None,
        min_matches: int = 1,
        max_matches: int = None,
        **kwargs,
    ) -> List[Alarm]:
        """
        Assert a count of matching alarms

        Args:
            expected_text (str, optional): Expected matching text
            min_matches (int, optional): Expected minimum number of alarms. Defaults to 1.
            max_matches (int, optional): Expected maximum number of alarms. Defaults to None.

        Returns:
            List[Alarm]: List of matching alarms
        """
        source = kwargs.pop("source", self.context.device_id)
        alarms = self.context.client.alarms.get_all(source=source, **kwargs)

        matching_alarms = alarms
        if expected_text:
            text_pattern = re.compile(expected_text, re.IGNORECASE)
            matching_alarms = list(filter(lambda x: text_pattern.match(x.text), alarms))

        assert len(matching_alarms) >= min_matches, (
            "Alarm count is less than expected. "
            f"wanted={min_matches} (min)\n"
            f"got={len(matching_alarms)}\n\n"
            f"alarms:\n{matching_alarms}"
        )

        if max_matches is not None:
            assert len(matching_alarms) <= max_matches, (
                "Alarm count is more than expected. "
                f"wanted={max_matches} (max)\n"
                f"got={len(matching_alarms)}\n\n"
                f"alarms:\n{matching_alarms}"
            )

        return matching_alarms

    def assert_exists(self, alarm_id: str, **kwargs) -> Alarm:
        """Assert that an alarm exists and return it if found"""
        try:
            return self.context.client.alarms.get(alarm_id)
        except KeyError as ex:
            raise AlarmNotFound() from ex
