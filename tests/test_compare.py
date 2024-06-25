"""Compare tests
"""
import unittest
from c8y_test_core.compare import compare_dataclass
import re


class TestDataclassComparison(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_compare_objects(self):
        mo = {
            "type": "thin-edge.io",
            "name": "TST_run_brass_click",
            "owner": "device_TST_run_brass_click",
            "c8y_Agent": {
                "name": "thin-edge.io",
                "version": "1.1.2~154+gc1df00f",
                "url": "https://thin-edge.io",
            },
            "c8y_Availability": {
                "lastMessage": "2024-06-25T15:13:38.919Z",
                "status": "AVAILABLE",
            },
            "com_cumulocity_model_Agent": {},
            "c8y_IsDevice": {},
            "c8y_Connection": {"status": "CONNECTED"},
            "c8y_RequiredAvailability": {"responseInterval": 1},
            "c8y_SupportedOperations": [
                "c8y_DownloadConfigFile",
                "c8y_LogfileRequest",
                "c8y_RemoteAccessConnect",
                "c8y_Restart",
                "c8y_SoftwareUpdate",
                "c8y_UploadConfigFile",
            ],
            "c8y_SoftwareList": [
                {"softwareType": "apt", "name": "apt", "version": "2.6.1", "url": ""},
                {
                    "softwareType": "apt",
                    "name": "apt-transport-https",
                    "version": "2.6.1",
                    "url": "",
                },
                {
                    "softwareType": "apt",
                    "name": "c8y-firmware-plugin",
                    "version": "1.1.2~154+gc1df00f",
                    "url": "",
                },
                {
                    "softwareType": "apt",
                    "name": "c8y-remote-access-plugin",
                    "version": "1.1.2~154+gc1df00f",
                    "url": "",
                },
                {
                    "softwareType": "apt",
                    "name": "curl",
                    "version": "7.88.1-10+deb12u5",
                    "url": "",
                },
                {
                    "softwareType": "apt",
                    "name": "mosquitto",
                    "version": "2.0.18-1+b2",
                    "url": "",
                },
                {
                    "softwareType": "apt",
                    "name": "mosquitto-clients",
                    "version": "2.0.18-1+b2",
                    "url": "",
                },
                {
                    "softwareType": "apt",
                    "name": "ssh",
                    "version": "1:9.7p1-5",
                    "url": "",
                },
                {
                    "softwareType": "apt",
                    "name": "sudo",
                    "version": "1.9.13p3-1+deb12u1",
                    "url": "",
                },
                {
                    "softwareType": "apt",
                    "name": "tedge",
                    "version": "1.1.2~154+gc1df00f",
                    "url": "",
                },
                {
                    "softwareType": "apt",
                    "name": "tedge-agent",
                    "version": "1.1.2~154+gc1df00f",
                    "url": "",
                },
                {
                    "softwareType": "apt",
                    "name": "tedge-apt-plugin",
                    "version": "1.1.2~154+gc1df00f",
                    "url": "",
                },
                {
                    "softwareType": "apt",
                    "name": "tedge-mapper",
                    "version": "1.1.2~154+gc1df00f",
                    "url": "",
                },
                {
                    "softwareType": "apt",
                    "name": "tedge-watchdog",
                    "version": "1.1.2~154+gc1df00f",
                    "url": "",
                },
                {
                    "softwareType": "apt",
                    "name": "vim-common",
                    "version": "2:9.0.1378-2",
                    "url": "",
                },
                {
                    "softwareType": "apt",
                    "name": "vim-tiny",
                    "version": "2:9.0.1378-2",
                    "url": "",
                },
                {
                    "softwareType": "apt",
                    "name": "wget",
                    "version": "1.21.3-1+b1",
                    "url": "",
                },
            ],
            "c8y_SupportedLogs": ["software-management"],
            "c8y_SupportedConfigurations": [
                "/etc/tedge/tedge.toml",
                "system.toml",
                "tedge-configuration-plugin",
            ],
        }
        assert compare_dataclass(mo, {"c8y_Availability": {"status": "AVAILABLE"}})
        assert not compare_dataclass(
            mo, {"c8y_Availability": {"status": "UNAVAILABLE"}}
        )
        assert compare_dataclass(
            mo,
            {
                "type": "thin-edge.io",
                "c8y_Agent": {
                    "name": "thin-edge.io",
                    "version": re.compile("^1.1.2.+"),
                },
            },
        )
        assert compare_dataclass(
            mo,
            {
                "c8y_SupportedConfigurations": [
                    "/etc/tedge/tedge.toml",
                    "system.toml",
                    "tedge-configuration-plugin",
                ],
            },
        )

        # out of order array
        assert not compare_dataclass(
            mo,
            {
                "c8y_SupportedConfigurations": [
                    "system.toml",
                    "/etc/tedge/tedge.toml",
                    "tedge-configuration-plugin",
                ],
            },
        )


if __name__ == "__main__":
    unittest.main()
