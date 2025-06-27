"""Inventory assertions
"""
import logging
from typing import Any, Dict, List, Optional
from c8y_api.model import ManagedObject
from c8y_test_core.assert_device import AssertDevice
from c8y_test_core.compare import compare_dataclass
from c8y_test_core.errors import FinalAssertionError


log = logging.getLogger()


class InventoryNotFound(AssertionError):
    """Inventory not found"""


class InventoryFound(AssertionError):
    """Inventory found"""


class AssertInventory(AssertDevice):
    """Inventory assertions"""

    def assert_exists(
        self, inventory_id: Optional[str] = None, **kwargs
    ) -> ManagedObject:
        """Assert that an inventory managed object exists
        Args:
            inventory_id (str, optional): managed object to check if it exists. If None
                then the device_id in the context will be used.
        """
        try:
            if inventory_id is None:
                inventory_id = self.context.device_id

            return self.context.client.inventory.get(inventory_id)
        except KeyError as ex:
            raise InventoryNotFound from ex

    def assert_not_exists(self, inventory_id: Optional[str] = None, **kwargs) -> None:
        """Assert that an inventory managed object does not exist

        Args:
            inventory_id (str, optional): managed object to check if it exists. If None
                then the device_id in the context will be used.
        """
        try:
            if inventory_id is None:
                inventory_id = self.context.device_id

            # expected to throw an error
            self.context.client.inventory.get(inventory_id)
            raise InventoryFound()
        except KeyError:
            return

    def assert_contains_supported_operations(
        self, *types: str, **kwargs
    ) -> ManagedObject:
        """Assert presence of some supported operations by checking the c8y_SupportedOperations
        fragment of the inventory managed object.

        It will only check if the given supported operations exist, other supported operations
        are allows to also exist which are not included in the assertion.

        Args:
            *types (str): List of expected supported operations

        Returns:
            ManagedObject: Managed object
        """
        mo = self.assert_contains_fragments(
            ["c8y_SupportedOperations"], mo=kwargs.pop("mo", None)
        )
        mo_dict = mo.to_json()

        missing = [
            typeName
            for typeName in types
            if typeName not in mo_dict["c8y_SupportedOperations"]
        ]
        assert len(missing) == 0, (
            "c8y_SupportedOperations is missing expected operations.\n"
            f"missing={missing}\n"
            f"got={mo_dict['c8y_SupportedOperations']}"
        )
        return mo

    def assert_supported_operations(self, *types: str, **kwargs) -> ManagedObject:
        """Assert exact supported operations by checking the c8y_SupportedOperations
        fragment of the inventory managed object.

        Args:
            *types (str): List of expected supported operations

        Returns:
            ManagedObject: Managed object
        """
        mo = self.assert_contains_fragments(
            ["c8y_SupportedOperations"], mo=kwargs.pop("mo", None)
        )
        mo_dict = mo.to_json()
        sortedTypes = sorted(types)
        actualTypes = sorted(mo_dict["c8y_SupportedOperations"])
        assert (
            sortedTypes == actualTypes
        ), f"c8y_SupportedOperations does not match.\nexpected={sortedTypes}\ngot={actualTypes}"
        return mo

    def assert_contains_fragment_values(
        self,
        fragments: Dict[str, Any],
        mo: Optional[ManagedObject] = None,
        **kwargs,
    ) -> ManagedObject:
        """Assert the present and the values of fragments in the device managed object"""
        if mo is None:
            mo = self.context.client.inventory.get(self.context.device_id)

        if not fragments:
            raise FinalAssertionError(
                "At least 1 fragment is required to compare objects"
            )

        assert compare_dataclass(mo.to_json(), fragments), (
            "Managed object does not contain fragment values\n"
            f"  wanted={fragments}\n"
            f"  got={mo.to_json()}"
        )
        return mo

    def assert_contains_fragments(
        self,
        fragments: List[str],
        mo: Optional[ManagedObject] = None,
        **kwargs,
    ) -> ManagedObject:
        """Assert the present of fragments in the device managed object (regardless of value)"""
        if mo is None:
            mo = self.context.client.inventory.get(self.context.device_id)

        mo_dict = mo.to_json()
        missing = [key for key in fragments if key not in mo_dict]
        assert (
            missing == []
        ), f"Device is missing some fragments. wanted={missing}, got={list(mo_dict.keys())}"
        return mo

    def assert_missing_fragments(
        self,
        fragments: List[str],
        mo: Optional[ManagedObject] = None,
        **kwargs,
    ) -> ManagedObject:
        """Assert the absence of fragments in a managed object

        Args:
            fragments (List[str]): List of fragments that should not be present on the
                device's managed object
            mo (ManagedObject, optional): Managed object to check
        """
        if mo is None:
            mo = self.context.client.inventory.get(self.context.device_id)

        mo_dict = mo.to_json()
        existing = [key for key in fragments if key in mo_dict]
        assert (
            existing == []
        ), f"Device is missing some fragments. wanted=[], got={existing}"
        return mo

    def assert_changed(
        self,
        reference_object: Dict[str, Any],
        fragment: str,
        mo: Optional[ManagedObject] = None,
        **kwargs,
    ) -> ManagedObject:
        """Assert that the device managed object has changed from the given reference object.
        The comparison is limited to a fragment if it is provided.
        """
        reference = reference_object.get(fragment) if fragment else reference_object

        if mo is None:
            mo = self.context.client.inventory.get(self.context.device_id)
        assert not compare_dataclass(mo.to_json().get(fragment), reference)
        return mo

    def assert_child_device_count(
        self, min_count: int = 1, max_count: Optional[int] = None, **kwargs
    ) -> List[Dict[str, Any]]:
        """Assert that a device has a specific number of child devices"""
        response = self.context.client.get(
            f"/inventory/managedObjects/{self.context.device_id}/childDevices",
            params={
                "pageSize": 2000,
            },
        )

        children = response.get("references", [])

        if min_count is not None:
            assert (
                len(children) >= min_count
            ), f"Expected total child devices count to be greater than or equal to {min_count}"

        if max_count is not None:
            assert (
                len(children) <= max_count
            ), f"Expected total child devices count to be less than or equal to {max_count}"

        return children

    def assert_child_device_names(
        self, *expected_devices: str, **kwargs
    ) -> List[Dict[str, Any]]:
        """Assert that a device has child devices with the specified names"""
        response = self.context.client.get(
            f"/inventory/managedObjects/{self.context.device_id}/childDevices"
        )

        children = []
        for child in response.get("references", []):
            child_mo = child.get("managedObject", {})
            if child_mo:
                children.append(child_mo)

        assert sorted(expected_devices) == sorted(map(lambda x: x["name"], children))
        return children

    def assert_no_child_devices(self, **kwargs):
        """Assert that a device has no child devices"""
        result_json = self.context.client.get(
            f"/inventory/managedObjects/{self.context.device_id}/childDevices",
            params={
                "pageSize": 1,
                "withTotalPages": "true",
            },
        )
        total = result_json["statistics"]["totalPages"]
        assert total == 0, (
            "Managed object should not have any child devices\n"
            "want=0\n"
            f"got={total}"
        )

    def assert_relationship(
        self,
        child_identity: str,
        child_identity_type: str = "c8y_Serial",
        child_type: str = "childDevices",
        mo: Optional[ManagedObject] = None,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """Assert that a child identity is a child of a give managed object

        Args:
            child_identity (str): Child identity name
            child_identity_type (str, optional): Child identity type. Defaults to 'c8y_Serial'
            child_type (str, optional): Child relationship type, e.g. childDevices, childAssets, childAdditions.
                Defaults to 'childDevices'
            mo (ManagedObject, optional): Managed Object (parent) object. If set to None, then the
                current context is used.
        """

        child_id = ""
        try:
            child_identity_obj = self.context.client.identity.get(
                child_identity, child_identity_type
            )
            child_id = child_identity_obj.managed_object_id
            assert child_id, "Child id should not be empty"
        except KeyError as ex:
            raise InventoryNotFound from ex

        try:
            mo_id = self.context.device_id
            if mo is not None:
                mo_id = mo.id
            return self.context.client.get(
                f"/inventory/managedObjects/{mo_id}/{child_type}/{child_id}"
            )  # type: ignore
        except KeyError as ex:
            raise InventoryNotFound from ex

    def delete_device_and_user(
        self,
        external_id: str,
        external_type: str = "c8y_Serial",
        **kwargs,
    ) -> None:
        """Assert device user and all child devices. The device user is then deleted afterwards"""

        try:
            mo_id = self.context.client.identity.get_id(external_id, external_type)
            log.info(
                "Removing managed object and all child devices. id=%s",
                mo_id,
            )
            self.context.client.delete(
                f"/inventory/managedObjects/{mo_id}",
                params={
                    "cascade": True,
                    "withDeviceUser": False,
                },
            )
        except KeyError as ex:
            log.info("Device has already been removed. %s", ex)
        except Exception as ex:
            log.error("Could not delete device. %s", ex)
            raise

        # delete the device user
        username = f"device_{external_id}"
        try:
            log.info("Removing device user. name=%s", username)
            tenant_id = self.context.client.tenant_id
            self.context.client.delete(f"/user/{tenant_id}/users/{username}")
        except KeyError as ex:
            log.info(
                "Device user has already been removed. name=%s, ex=%s", username, ex
            )
        except Exception as ex:
            log.error("Could not delete device user. name=%s, ex=%s", username, ex)
            raise

    def get_services(
        self,
        inventory_id,
        service_type: Optional[str] = None,
        status: Optional[str] = None,
        name: Optional[str] = None,
        query: Optional[str] = None,
        page_size: int = 100,
    ) -> List[ManagedObject]:
        """Get services attached to a specific device

        Args:
            inventory_id (str, optional): managed object to check if it exists. If None
                then the device_id in the context will be used.
            min_count (int, optional): Minimum number of service matches (inclusive)
            max_count (int, optional): Maximum number of service matches (inclusive)
            service_type (str, optional): Filter by service type
            name (str, optional): Filter by service name
            status (str, optional): Filter by service status
            query (str, optional): Use custom inventory query language
            page_size (int, optional): Maximum number of page results to return

        Returns:
            List[ManagedObject]: List of services
        """
        query_parts = ["(type eq 'c8y_Service')"]

        if service_type:
            query_parts.append(f"(serviceType eq '{service_type}')")

        if status:
            query_parts.append(f"(status eq '{status}')")

        if name:
            query_parts.append(f"(name eq '{name}')")

        if query:
            query_parts.append(query)

        query_str = "$filter=" + " and ".join(query_parts)

        try:
            url = (
                self.context.client.inventory.build_object_path(inventory_id)
                + "/childAdditions"
            )
            response = self.context.client.get(
                url,
                params={
                    "query": query_str,
                    "pageSize": page_size,
                },
            )
            children = [
                ManagedObject.from_json(ref["managedObject"])
                for ref in response.get("references", [])
            ]
            return children
        except KeyError as ex:
            # 404 errors
            raise InventoryNotFound from ex

    def assert_services(
        self,
        inventory_id: Optional[str] = None,
        min_count: int = 1,
        max_count: Optional[int] = None,
        service_type: Optional[str] = None,
        status: Optional[str] = None,
        name: Optional[str] = None,
        **kwargs,
    ) -> List[ManagedObject]:
        """Assert services attached to a specific device

        Args:
            inventory_id (str, optional): managed object to check if it exists. If None
                then the device_id in the context will be used.
            min_count (int, optional): Minimum number of service matches (inclusive)
            max_count (int, optional): Maximum number of service matches (inclusive)
            service_type (str, optional): Filter by service type
            name (str, optional): Filter by service name
            status (str, optional): Filter by service status

        Returns:
            List[ManagedObject]: List of services
        """
        if inventory_id is None:
            inventory_id = self.context.device_id
        services = (
            self.get_services(
                inventory_id, service_type=service_type, status=status, name=name
            )
            or []
        )

        if min_count is not None:
            assert (
                len(services) >= min_count
            ), f"Expected total device services count to be greater than or equal to {min_count}"

        if max_count is not None:
            assert (
                len(services) <= max_count
            ), f"Expected total device services count to be less than or equal to {max_count}"

        return services

    def create_managed_object(
        self,
        type: Optional[str] = None,
        name: Optional[str] = None,
        owner: Optional[str] = None,
        fragments: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> ManagedObject:
        """Create a managed object

        Args:
            name (str, optional): Name
            type (str, optional): Type
            owner (str, optional): Owner
            fragments (Dict[str, Any], optional): Additional fragments to include

        Returns:
            ManagedObject: The created managed object
        """
        if not fragments:
            fragments = {}

        mo = ManagedObject(
            self.context.client, type=type, name=name, owner=owner, **fragments  # type: ignore
        ).create()
        return mo
