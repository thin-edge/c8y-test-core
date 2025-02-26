"""Measurement assertions"""
from typing import Any, List

from c8y_api.model import ManagedObject, Measurement

from c8y_test_core.assert_device import AssertDevice
from c8y_test_core.errors import FinalAssertionError


class AssertMeasurements(AssertDevice):
    """Measurement assertions"""

    def _get_supported_series(self) -> List[str]:
        response = self.context.client.get(
            f"/inventory/managedObjects/{self.context.device_id}/supportedSeries"
        )
        return response["c8y_SupportedSeries"]

    def assert_supported_series_contains(
        self, *expected_series: str, **kwargs
    ) -> ManagedObject:
        """Assert presence of a subset of series in the supported series list"""
        missing = []
        current_series = self._get_supported_series()
        for name in expected_series:
            if name not in current_series:
                missing.append(name)

        assert (
            len(missing) == 0
        ), f"Device is missing some series. wanted={expected_series}, got={current_series}"

    def assert_supported_series(
        self,
        *expected_series: str,
        **kwargs,
    ) -> ManagedObject:
        """Assert exact supported series"""

        wanted = sorted(expected_series)
        got = sorted(self._get_supported_series())
        assert got == wanted, f"wanted={wanted}, got={got}"

    def assert_count(
        self,
        min_count: int = 1,
        max_count: int = None,
        **kwargs,
    ) -> List[Any]:
        """Assert a measurement count

        Args:
            min_count (int, optional): Minimum (inclusive) number of matches.
                Ignored if set to None. Defaults to 1.
            max_count (int, optional): Maximum (inclusive) number of matches.
                Ignored if set to None. Defaults to None.

        Returns:
            List[Any]: List of measurements
        """
        source = kwargs.pop("source", self.context.device_id) or None
        if not source:
            raise FinalAssertionError(
                "source and the current device context is empty. One of these values must be set!"
            )
        page_size = kwargs.pop("pageSize", 2000)

        measurements = self.context.client.measurements.get_all(
            source=source,
            page_size=page_size,
            **kwargs,
        )

        total = len(measurements)

        if min_count is not None and max_count is not None:
            assert min_count <= total <= max_count
        elif min_count is not None and max_count is None:
            assert total >= min_count
        elif min_count is None and max_count is not None:
            assert total <= max_count

        return measurements
