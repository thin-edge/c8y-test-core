"""Custom Cumulocity API app
"""
import logging
import os

from c8y_api._auth import HTTPBearerAuth
from c8y_api.app import CumulocityApi, _CumulocityAppBase
from requests.auth import HTTPBasicAuth


class CustomCumulocityApp(_CumulocityAppBase, CumulocityApi):
    """Application-like Cumulocity API.

    The SimpleCumulocityApp class is intended to be used as base within
    a single-tenant micro service hosted on Cumulocity. It evaluates the
    environment to teh resolve the authentication information automatically.

    Note: This class should be used in Cumulocity micro services using the
    PER_TENANT authentication mode only. It will not function in environments
    using the MULTITENANT mode.

    The SimpleCumulocityApp class is an enhanced version of the standard
    CumulocityApi class. All Cumulocity functions can be used directly.
    Additionally it can be used to provide CumulocityApi instances for
    specific named users via the `get_user_instance` function.
    """

    log = logging.getLogger(__name__)

    def __init__(
        self, application_key: str = None, cache_size: int = 100, cache_ttl: int = 3600
    ):
        """Create a new tenant specific instance.

        Args:
            application_key (str|None): An application key to include in
                all requests for tracking purposes.
            cache_size (int|None): The maximum number of cached user
                instances (if user instances are created at all).
            cache_ttl (int|None): An maximum cache time for user
                instances (if user instances are created at all).

        Returns:
            A new CumulocityApp instance
        """
        baseurl = self._get_env("C8Y_BASEURL")

        username = self._get_env("C8Y_USER")

        tenant_id = ""
        if "C8Y_TENANT" in os.environ:
            tenant_id = self._get_env("C8Y_TENANT")

        if "C8Y_PASSWORD" in os.environ:
            password = self._get_env("C8Y_PASSWORD")
            auth = HTTPBasicAuth(username, password)
        elif "C8Y_TOKEN" in os.environ:
            token = self._get_env("C8Y_TOKEN")
            auth = HTTPBearerAuth(token)
        else:
            raise Exception("Unknown authorization")

        super().__init__(
            log=self.log,
            cache_size=cache_size,
            cache_ttl=cache_ttl,
            base_url=baseurl,
            tenant_id=tenant_id,
            auth=auth,
            application_key=application_key,
        )

    def _build_user_instance(self, auth) -> CumulocityApi:
        """Build a CumulocityApi instance for a specific user, using the
        same Base URL, Tenant ID and Application Key as the main instance."""
        return CumulocityApi(
            base_url=self.base_url,
            tenant_id=self.tenant_id,
            auth=auth,
            application_key=self.application_key,
        )
