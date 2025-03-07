"""
mlte/store/custom_list/underlying/fs.py

Implementation of local file system custom list store.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from mlte.custom_list.custom_list_names import CustomListName
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
        self._set_base_path(list_name)
        self.storage.ensure_resource_does_not_exist(entry.name)
        return self._write_entry(entry)

    def edit(
        self,
        entry: CustomListEntryModel,
        list_name: Optional[CustomListName] = None,
    ) -> CustomListEntryModel:
        self._set_base_path(list_name)
        self.storage.ensure_resource_exists(entry.name)
        return self._write_entry(entry)

    def read(
        self, entry_name: str, list_name: Optional[CustomListName] = None
    ) -> CustomListEntryModel:
        self._set_base_path(list_name)
        return self._read_entry(entry_name)

    def list(self, list_name: Optional[CustomListName] = None) -> List[str]:
        self._set_base_path(list_name)
        return self.storage.list_resources()

    def delete(
        self, entry_name: str, list_name: Optional[CustomListName] = None
    ) -> CustomListEntryModel:
        self._set_base_path(list_name)
        self.storage.ensure_resource_exists(entry_name)
        entry = self._read_entry(entry_name)
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
        Sets the path to the list specified in the param.

        This method sets the base path of the mapper to the path of the list given as a param.
        This has to happen before each request to ensure that the operation happens on the correct list.
        """
        if CustomListName is not None:
            self.storage.set_base_path(
                Path(self.storage.sub_folder, str(list_name))
            )
        else:
            raise ValueError("CustomListName cannot be None")
