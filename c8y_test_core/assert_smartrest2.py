"""SmartREST 2.0 assertions
"""
import logging
from typing import Any, Dict, List, Optional
from c8y_api.model import ManagedObject
from c8y_test_core.assert_device import AssertDevice
from c8y_test_core.compare import compare_dataclass
from c8y_test_core.errors import FinalAssertionError


log = logging.getLogger()

SMARTREST2_EXTERNAL_ID_TYPE = "c8y_SmartRest2DeviceIdentifier"
SMARTREST2_MANAGED_OBJECT_TYPE = "c8y_SmartRest2Template"


class SmartREST2TemplateNotFound(AssertionError):
    """SmartREST 2.0 Template not found"""


class SmartREST2TemplateFound(AssertionError):
    """SmartREST 2.0 Template found"""


class AssertSmartREST2(AssertDevice):
    """SmartREST 2.0 assertions"""

    def assert_exists(self, external_id: str, **kwargs) -> ManagedObject:
        """Assert that a SmartREST 2.0 template collection exists
        Args:
            external_id (str): external id to check if it exists
        """
        try:
            return self.context.client.identity.get_object(
                external_id, SMARTREST2_EXTERNAL_ID_TYPE
            )
        except KeyError as ex:
            raise SmartREST2TemplateNotFound from ex

    def assert_not_exists(self, external_id: str, **kwargs) -> None:
        """Assert that a SmartREST 2.0 template collection does not exist

        Args:
            external_id (str): external id to check if it does not exist
        """
        try:
            # expected to throw an error
            self.context.client.identity.get_object(
                external_id, SMARTREST2_EXTERNAL_ID_TYPE
            )
            raise SmartREST2TemplateFound()
        except KeyError:
            return

    def create(
        self,
        name: str,
        fragments: Dict[str, Any],
        **kwargs,
    ) -> ManagedObject:
        """Create a SmartREST 2.0 Template Collection

        Args:
            name (str): Name (also used as the external id)
            fragments (Dict[str, Any]): Additional fragments to include

        Returns:
            ManagedObject: The created SmartREST 2 object (managed object)
        """
        if not fragments:
            fragments = {}

        data = {
            **fragments,
            "__externalId": name,
        }

        mo = ManagedObject(
            self.context.client, type=SMARTREST2_MANAGED_OBJECT_TYPE, name=name, **data
        ).create()

        self.context.client.identity.create(name, SMARTREST2_EXTERNAL_ID_TYPE, mo.id)

        return mo
