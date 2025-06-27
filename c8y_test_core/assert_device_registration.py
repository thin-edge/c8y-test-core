"""Device registration assertions and actions"""
import io
import logging
import random
import secrets
import time
from dataclasses import dataclass
from typing import Optional
from c8y_test_core.assert_device import AssertDevice
from c8y_test_core.utils import to_csv
import contextlib


@dataclass
class DeviceCredentials:
    """Device credentials"""

    url: str
    username: str
    password: str


@dataclass
class DeviceSimpleEnrollCredentials:
    """Device enrollment credentials for the Cumulocity certificate-authority feature"""

    url: str
    external_id: str
    one_time_password: str


log = logging.getLogger()


def random_password(password_len=16) -> str:
    """Generate random password the fulfils the default
    Cumulocity password policy.

    Args:
        password_len (int, optional): Password length. Defaults to 16.

    Returns:
        str: Random password
    """
    lowercase = "".join(
        [secrets.choice("abcdefghijklmnopqrstuvwxyz") for i in range(0, 2)]
    )
    uppercase = "".join(
        [secrets.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for i in range(0, 2)]
    )
    digits = "".join([secrets.choice("0123456789") for i in range(0, 2)])
    # use url safe symbols
    symbols = "".join([secrets.choice("$-_.+!*(),") for i in range(0, 2)])
    password_requirements = "".join([lowercase, uppercase, digits, symbols])
    password = password_requirements + secrets.token_urlsafe(
        password_len - len(password_requirements) - 2
    )

    # randomize order of password
    value = "".join(random.sample(password, len(password)))

    # avoid starting the string with a dash as it can cause cli parsing problems for some
    # libraries
    if value.startswith("-"):
        value = "_" + value[1:]
    return value


class AssertDeviceRegistration(AssertDevice):
    """Assertions"""

    def bulk_register_with_basic_auth(
        self,
        external_id: str,
        external_type: str = "c8y_Serial",
        name: Optional[str] = None,
        device_type: str = "thin-edge.io",
        auth_type: str = "BASIC",
        **kwargs,
    ) -> DeviceCredentials:
        """Bulk device registration for device that require
        non-cert based authentication (e.g. basic auth)

        Arguments:
            external_id (str): External id
            external_type (str): External type. Defaults to c8y_Serial
            name (Optional[str]): Name of the device. Defaults to the external_id
            type (Optional[str]): Type of the device. Defaults to thin-edge.io
            auth_type (Optional[str]): Type of the authentication type.
                Either 'BASIC' or 'CREDENTIALS'. Defaults to 'BASIC'
        """
        name = name or external_id
        password = random_password()
        registration_body = to_csv(
            [
                ("ID", [external_id]),
                ("IDTYPE", [external_type]),
                ("AUTH_TYPE", [auth_type]),
                ("CREDENTIALS", [password]),
                ("TYPE", [device_type]),
                ("NAME", [name]),
                ("com_cumulocity_model_Agent.active", [True]),
            ]
        )

        resp = self.context.client.post_file(
            "/devicecontrol/bulkNewDeviceRequests",
            io.BytesIO(registration_body.encode("utf-8")),
            accept="application/json",
        )
        log.info("Registration response: %s", resp)
        assert resp["numberOfSuccessful"] == resp["numberOfAll"], (
            "Failed to register device\n" f"response:\n{resp}"
        )

        username = f"device_{external_id}"
        if self.context.client.tenant_id:
            username = f"{self.context.client.tenant_id}/device_{external_id}"

        return DeviceCredentials(
            username=username, password=password, url=self.context.domain()
        )

    def bulk_register_with_ca(
        self,
        external_id: str,
        external_type: str = "c8y_Serial",
        name: Optional[str] = None,
        device_type: str = "thin-edge.io",
        **kwargs,
    ) -> DeviceSimpleEnrollCredentials:
        """Bulk device registration using the Cumulocity
        certificate-authority feature

        Arguments:
            external_id (str): External id
            external_type (str): External type. Defaults to c8y_Serial
            name (Optional[str]): Name of the device. Defaults to the external_id
            type (Optional[str]): Type of the device. Defaults to thin-edge.io
        """
        name = name or external_id
        one_time_password = random_password()
        registration_body = to_csv(
            [
                ("ID", [external_id]),
                ("IDTYPE", [external_type]),
                ("AUTH_TYPE", ["CERTIFICATES"]),
                ("ENROLLMENT_OTP", [one_time_password]),
                ("TYPE", [device_type]),
                ("NAME", [name]),
                ("com_cumulocity_model_Agent.active", [True]),
            ]
        )

        # Remove any existing request as you can't update existing credentials (ignore 404 errors)
        with contextlib.suppress(KeyError):
            self.context.client.delete(
                f"/devicecontrol/bulkNewDeviceRequests/{external_id}"
            )

        resp = self.context.client.post_file(
            "/devicecontrol/bulkNewDeviceRequests",
            io.BytesIO(registration_body.encode("utf-8")),
            accept="application/json",
        )
        log.info("Registration response: %s", resp)
        assert resp["numberOfSuccessful"] == resp["numberOfAll"], (
            "Failed to register device\n" f"response:\n{resp}"
        )

        return DeviceSimpleEnrollCredentials(
            external_id=external_id,
            one_time_password=one_time_password,
            url=self.context.domain(),
        )

    def register_with_basic_auth(self, external_id: str, timeout: float = 60, **kwargs):
        """Register a single device using the basic auth

        For the registration to work, the device must be polling the
        POST /devicecontrol/newDeviceRequests/{external_id} endpoint in the background.
        Once the request is approved by this function, the device will receive
        platform credentials.

        Arguments:
            external_id (str): external id of the device to be registered
            timeout (float): Timeout in seconds. Defaults to 60
        """
        resp = self.context.client.post(
            "/devicecontrol/newDeviceRequests",
            json={
                "id": external_id,
            },
            accept="application/json",
        )
        log.info("Registration response. %s", resp)

        # pylint: disable=broad-exception-caught
        success = False
        timeout_at = time.monotonic() + timeout
        while True:
            try:
                resp = self.context.client.put(
                    f"/devicecontrol/newDeviceRequests/{external_id}",
                    json={
                        "status": "ACCEPTED",
                    },
                    accept="application/json",
                    content_type="application/json",
                )
                log.info("Registration accepted: %s", resp)
                success = True
                break
            except Exception as ex:
                log.info(
                    "Registration accepted failed: response=%s, exception=%s", resp, ex
                )
            time.sleep(3)
            if time.monotonic() > timeout_at:
                break

        assert success, "Failed to register device"
