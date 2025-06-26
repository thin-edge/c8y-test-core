"""Device certificate assertions"""
import logging
import re
from typing import Any, Dict, Optional

from c8y_test_core.assert_device import AssertDevice


log = logging.getLogger()


class AssertDeviceCertificate(AssertDevice):
    """Assertions"""

    def upload_certificate(
        self,
        name: str,
        pem_cert: str,
        ignore_duplicate: bool = True,
        **kwargs,
    ) -> Optional[Dict[str, Any]]:
        """Upload a trusted certificate to Cumulocity

        Args:
            name (str): Name of the certificate
            pem_cert (str): Contents of a x509 certificate
                in the PEM format. headers and whitespace will be stripped
            ignore_duplicate (bool, optional): Ignore errors if the certificate
                has already been uploaded. No response will be returned in this case.

        Returns:
            Optional[Dict[str, Any]]: Response if the certificate is uploaded
                any errors
        """
        contents = pem_cert.replace("-----BEGIN CERTIFICATE-----", "")
        contents = contents.replace("-----END CERTIFICATE-----", "")
        contents = re.sub(r"\s", "", contents, 0, re.MULTILINE)

        tenant_id = self.context.client.tenant_id
        try:
            response = self.context.client.post(
                f"/tenant/tenants/{tenant_id}/trusted-certificates",
                {
                    "name": name,
                    "status": "ENABLED",
                    "certInPemFormat": contents,
                },
            )
            return response
        except ValueError as ex:
            if ignore_duplicate and "409" in str(ex):
                log.info("Certificate has already been uploaded. %s", ex)
                return None
            raise

    def delete_certificate(
        self,
        fingerprint: str,
        **kwargs,
    ) -> None:
        """Assert device certificate"""
        try:
            log.info("Removing device certificate. fingerprint=%s", fingerprint)
            if not self.context.client.tenant_id:
                raise ValueError(f"tenant_id is not set in api client")
            self.context.client.delete(
                (
                    f"/tenant/tenants/{self.context.client.tenant_id}"
                    f"/trusted-certificates/{fingerprint}"
                ),
            )
        except KeyError as ex:
            log.info("Certificate does not exist, so nothing to delete. ex=%s", ex)
        except ValueError as ex:
            log.error("Could not delete device certificate. ex=%s", ex)
            raise
        return
