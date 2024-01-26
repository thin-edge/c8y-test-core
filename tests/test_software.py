"""Software assertion tests
"""
import unittest
from typing import List, Dict
from c8y_test_core import assert_software_management
from c8y_api.model.inventory import ManagedObject
from c8y_test_core.models import Software
from .fixtures import create_context


def create_mo_with_software(software: List[Dict[str, str]]):
    mo = ManagedObject()
    mo["c8y_SoftwareList"] = [item for item in software]
    return mo


class TestSoftwareInstalled(unittest.TestCase):
    def setUp(self) -> None:
        self.software = assert_software_management.SoftwareManagement(create_context())
        return super().setUp()

    def test_package_is_installed(self):
        mo = create_mo_with_software(
            [
                {"name": "package1", "version": "1.0.0", "url": ""},
            ]
        )
        self.software.assert_software_installed(
            Software("package1"), mo=mo, timeout=0.01
        )
        self.software.assert_software_installed(
            Software(name="package1", version="1.0.0"), mo=mo, timeout=0.01
        )

        with self.assertRaisesRegex(AssertionError, "VERSION_MISMATCH"):
            self.software.assert_software_installed(
                Software(name="package1", version="1.0.1"), mo=mo, timeout=0.01
            )

    def test_version_regex_match(self):
        mo = create_mo_with_software(
            [
                {"name": "package1", "version": "1.0.0~10+deb12"},
            ]
        )
        self.software.assert_software_installed(
            Software("package1", version=r"1\.[0-9]+\.[0-9].*"), mo=mo, timeout=0.01
        )

        with self.assertRaisesRegex(AssertionError, "VERSION_MISMATCH"):
            self.software.assert_software_installed(
                Software("package1", version=r".+deb11"), mo=mo, timeout=0.01
            )

    def test_package_is_installed_match_by_type(self):
        mo = create_mo_with_software(
            [
                {"name": "package1", "version": "1.0.0", "type": "apt"},
            ]
        )
        self.software.assert_software_installed(
            Software("package1", version=r"1\.[0-9]+\.[0-9]", type="apt"),
            mo=mo,
            timeout=0.01,
        )

        with self.assertRaisesRegex(AssertionError, "TYPE_MATCH"):
            self.software.assert_software_installed(
                Software("package1", version=r"1\.[0-9]+\.[0-9]", type="debian"),
                mo=mo,
                timeout=0.01,
            )

    def test_package_is_installed_error(self):
        mo = create_mo_with_software(
            [
                {"name": "package1", "version": "1.0.0", "url": ""},
            ]
        )
        with self.assertRaisesRegex(AssertionError, "MISSING"):
            self.software.assert_software_installed(
                Software("packageOther"), mo=mo, timeout=0.01
            )


class TestSoftwareNotInstalled(unittest.TestCase):
    def setUp(self) -> None:
        self.software = assert_software_management.SoftwareManagement(create_context())
        return super().setUp()

    def test_name_does_not_exist(self):
        mo = create_mo_with_software(
            [
                {"name": "package1", "version": "1.0.0", "url": ""},
            ]
        )
        self.software.assert_not_software_installed(
            Software("package2"), mo=mo, timeout=0.01
        )

        with self.assertRaisesRegex(AssertionError, "INSTALLED"):
            self.software.assert_not_software_installed(
                Software("package1"), mo=mo, timeout=0.01
            )

    def test_version_does_not_match(self):
        mo = create_mo_with_software(
            [
                {"name": "package1", "version": "1.0.0", "url": ""},
            ]
        )

        self.software.assert_not_software_installed(
            Software("package1", version="2.0.0"), mo=mo, timeout=0.01
        )

        with self.assertRaisesRegex(AssertionError, "VERSION_MATCH"):
            self.software.assert_not_software_installed(
                Software("package1", version="1.0.0"), mo=mo, timeout=0.01
            )


if __name__ == "__main__":
    unittest.main()
