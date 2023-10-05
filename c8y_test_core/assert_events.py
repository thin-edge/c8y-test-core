"""Event assertions"""
import hashlib
import re
from typing import List, Union

from c8y_api.model import Event

from c8y_test_core.assert_device import AssertDevice
from . import compare


class EventNotFound(AssertionError):
    """Event not found"""


class Events(AssertDevice):
    """Event assertions"""

    # pylint: disable=too-few-public-methods

    def assert_count(
        self,
        expected_text: str = None,
        min_matches: int = 1,
        max_matches: int = None,
        with_attachment: bool = None,
        **kwargs,
    ) -> List[Event]:
        """Assert a minimum count of matches events.

        Args:
            expected_text (str, optional): Expected matching text
            min_matches (int, optional): Expected minimum number of events. Defaults to 1.
            max_matches (int, optional): Expected maximum number of events. Defaults to None.
            with_attachment (bool, optional): Only match events with an attachment.
                If set to True, it will override any 'fragment' kwargs provided!

        Returns:
            List[Event]: List of matching events
        """
        source = kwargs.pop("source", self.context.device_id)

        fragment = kwargs.pop("fragment", None)
        if with_attachment:
            # Override the existing fragment check
            fragment = "c8y_IsBinary"

        events = self.context.client.events.get_all(
            source=source, fragment=fragment, **kwargs
        )

        matching_events = events
        if expected_text:
            text_pattern = re.compile(expected_text, re.IGNORECASE)
            matching_events = list(filter(lambda x: text_pattern.match(x.text), events))

        assert len(matching_events) >= min_matches, (
            "Event count is less than expected. "
            f"wanted={min_matches} (min), got={len(matching_events)}"
        )

        if max_matches is not None:
            assert len(matching_events) <= max_matches, (
                "Event count is more than expected. "
                f"wanted={max_matches} (max), got={len(matching_events)}"
            )
        return matching_events

    def assert_exists(self, event_id: str, **kwargs) -> Event:
        """Assert that an event exists and return it if found"""
        try:
            return self.context.client.events.get(event_id)
        except KeyError as ex:
            raise EventNotFound() from ex

    def assert_no_attachment(self, event_id: str) -> None:
        """Assert that the event id does not have an attachment

        Args:
            event_id (str): Event id
        """
        exists = False
        try:
            url = self.context.client.events.build_object_path(event_id) + "/binaries"
            self.context.client.get_file(url)
            exists = True
        except KeyError as ex:
            # 404 errors
            exists = False

        assert exists == False, "Attachment should not exist"

    def assert_attachment_info(
        self, event: Union[Event, str], expected_name_pattern: str = None, **kwargs
    ) -> Event:
        """Assert that the attachment meta information matches
        The meta information controls the name of the file when the user downloads it from
        the UI.

        Args:
            event (Event, str): Event or event id to check. If the users provides an event id
                it will be looked up.
            expected_name_pattern (str, optional): Expected name pattern. Ignored if set to None.

        Returns:
            Event: Event
        """

        if isinstance(event, str):
            event = self.context.client.events.get(event)

        data = event.to_json()
        assert "c8y_IsBinary" in data

        if expected_name_pattern is not None:
            name = data["c8y_IsBinary"]["name"]
            assert name == compare.RegexPattern(
                expected_name_pattern
            ), "Attachment name does not match"

        return event

    def assert_attachment(
        self,
        event_id: str,
        expected_contents: str = None,
        expected_pattern: str = None,
        expected_size_min: int = None,
        expected_md5: str = None,
        encoding: str = "utf8",
        **kwargs,
    ) -> bytes:
        """Assert that an event has an attachment

        Args:
            event_id (str, optional): Event id which should have an attachment (binary)
            expected_contents (str, optional): Expected contents (as a string) should exactly match against. Ignored if set to None.
            expected_pattern (str, optional): Expected regex pattern which the contents should match (using re.MULTILINE | re.DOTALL regex flags).
                Ignored if set to None
            expected_size_min (int, optional): Expected minimum size in bytes. Ignored if set to None.
            expected_md5 (str, optional): Expected md5 checksum of the file attachment.
                Defaults to None.
            encoding (str, optional): Encoding to be used when comparing the attachment contents. Defaults to 'utf8'

        Returns:
            bytes: Attachment bytes
        """

        url = self.context.client.events.build_object_path(event_id) + "/binaries"
        downloaded_file = self.context.client.get_file(url)

        if expected_size_min is not None:
            assert (
                len(downloaded_file) >= expected_size_min
            ), f"Expected file size to be greater or equal to {expected_size_min} bytes"

        # Compare contents (if provided by user)
        if expected_pattern is not None:
            contents = downloaded_file.decode(encoding)
            assert contents == compare.RegexPattern(
                expected_pattern, re.MULTILINE | re.DOTALL
            )
        elif expected_contents is not None:
            contents = downloaded_file.decode(encoding)
            assert contents == expected_contents

        # Compare checksums
        if expected_md5 is not None:
            file_md5 = hashlib.md5(downloaded_file).hexdigest().lower()
            assert expected_md5.lower() == file_md5, (
                "Event binary checksum (md5) did not match. "
                f"wanted={expected_md5.lower()}, got={file_md5}"
            )

        # Return raw bytes so the user can apply their own checks
        return downloaded_file
