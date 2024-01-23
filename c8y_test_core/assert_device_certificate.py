"""Device certificate assertions"""
import logging
from c8y_test_core.assert_device import AssertDevice


log = logging.getLogger()


class AssertDeviceCertificate(AssertDevice):
    """Assertions"""

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
