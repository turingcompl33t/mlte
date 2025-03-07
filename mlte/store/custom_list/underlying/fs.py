"""
mlte/store/custom_list/underlying/fs.py

Implementation of local file system custom list store.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import mlte.store.error as errors
from mlte.custom_list.custom_list_names import (
    CustomListName,
    CustomListParentMappings,
)
from mlte.custom_list.model import CustomListEntryModel
from mlte.store.base import StoreURI
from mlte.store.common.fs_storage import FileSystemStorage
from mlte.store.custom_list.store import CustomListStore
from mlte.store.custom_list.store_session import (
    CustomListEntryMapper,
    CustomListStoreSession,
)

# -----------------------------------------------------------------------------
# FileSystemCustomListStore
# -----------------------------------------------------------------------------


class FileSystemCustomListStore(CustomListStore):
    """A local file system implementation of the MLTE custom list store."""

    BASE_CUSTOM_LIST_FOLDER = "custom_lists"
    """Base folder to store custom lists in."""

    def __init__(self, uri: StoreURI) -> None:
        self.storage = FileSystemStorage(
            uri=uri, sub_folder=self.BASE_CUSTOM_LIST_FOLDER
        )
        """Underlying storage."""

        # Initialize defaults.
        super().__init__(uri=uri)

    def session(self) -> FileSystemCustomListStoreSession:
        """
        Return a session handle for the store instance.
        :return: The session handle
        """
        return FileSystemCustomListStoreSession(storage=self.storage)


# -----------------------------------------------------------------------------
# FileSystemCustomListStoreSession
# -----------------------------------------------------------------------------


class FileSystemCustomListStoreSession(CustomListStoreSession):
    """A local file-system implementation of the MLTE custom list store."""

    def __init__(self, storage: FileSystemStorage) -> None:
        self.custom_list_entry_mapper = FileSystemCustomListEntryMapper(storage)
        """The mapper to custom list entry CRUD."""

    def close(self) -> None:
        """Close the session."""
        # Closing a local FS session is a no-op.
        pass


# -----------------------------------------------------------------------------
# FileSystemCustomListEntryMappper
# -----------------------------------------------------------------------------


class FileSystemCustomListEntryMapper(CustomListEntryMapper):
    """FS mapper for the custom list entry resource."""

    def __init__(self, storage: FileSystemStorage) -> None:
        self.storage = storage.clone()
        """A reference to underlying storage."""

    def create(
        self,
        entry: CustomListEntryModel,
        list_name: Optional[CustomListName] = None,
    ) -> CustomListEntryModel:
        self._ensure_parent_exists(entry.parent, list_name)
        self._set_base_path(list_name)
        self.storage.ensure_resource_does_not_exist(entry.name)
        return self._write_entry(entry)

    def read(
        self, entry_name: str, list_name: Optional[CustomListName] = None
    ) -> CustomListEntryModel:
        self._set_base_path(list_name)
        return self._read_entry(entry_name)

    def list(self, list_name: Optional[CustomListName] = None) -> List[str]:
        self._set_base_path(list_name)
        return self.storage.list_resources()
    
    def edit(
        self,
        entry: CustomListEntryModel,
        list_name: Optional[CustomListName] = None,
    ) -> CustomListEntryModel:
        self._ensure_parent_exists(entry.parent, list_name)
        self._set_base_path(list_name)
        self.storage.ensure_resource_exists(entry.name)
        return self._write_entry(entry)

    def delete(
        self, entry_name: str, list_name: Optional[CustomListName] = None
    ) -> CustomListEntryModel:
        self._set_base_path(list_name)
        self.storage.ensure_resource_exists(entry_name)
        entry = self._read_entry(entry_name)

        if list_name in CustomListParentMappings.parent_mappings.values():
            child_list_name = list(
                CustomListParentMappings.parent_mappings.keys()
            )[
                list(CustomListParentMappings.parent_mappings.values()).index(
                    list_name
                )
            ]
            for child_entry_name in self.list(child_list_name):
                child_entry = self.read(child_entry_name, child_list_name)
                if child_entry.parent == entry_name:
                    self.delete(child_entry_name, child_list_name)

        self._set_base_path(list_name)
        self.storage.delete_resource(entry_name)
        return entry

    def _read_entry(self, entry_name: str) -> CustomListEntryModel:
        """Reads a custom list entry."""
        self.storage.ensure_resource_exists(entry_name)
        return CustomListEntryModel(**self.storage.read_resource(entry_name))

    def _write_entry(self, entry: CustomListEntryModel) -> CustomListEntryModel:
        """Writes a custom list entry to storage."""
        self.storage.write_resource(entry.name, entry.to_json())
        return self._read_entry(entry.name)

    def _set_base_path(self, list_name: Optional[CustomListName]) -> None:
        """
        Sets the path to the list specified in the param and checks list exists.

        This method sets the base path of the mapper to the path of the list given as a param.
        This has to happen before each request to ensure that the operation happens on the correct list.
        """
        if (
            list_name is None
            or list_name not in CustomListName._value2member_map_
        ):
            raise errors.ErrorNotFound(
                f"CustomListName, {list_name}, does not exist or is None."
            )
        else:
            self.storage.set_base_path(
                Path(self.storage.sub_folder, str(list_name))
            )

    def _ensure_parent_exists(
        self, parent: str, list_name: Optional[CustomListName]
    ) -> None:
        if list_name in CustomListParentMappings.parent_mappings.keys():
            if parent not in self.list(
                CustomListParentMappings.parent_mappings[list_name]
            ):
                raise errors.ErrorNotFound(
                    f"Parent {parent} does not exist in list {list_name}"
                )
        elif parent != "":
            raise errors.InternalError(
                "Parent specified for item in list with no parent list."
            )
