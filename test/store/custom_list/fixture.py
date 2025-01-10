"""
test/store/custom_list/fixture.py

Fixtures for MLTE custom list store unit tests.
"""

from __future__ import annotations

import typing
from typing import Generator, List
from pathlib import Path

import pytest

from mlte.custom_list.model import CustomListModel, CustomListEntryModel
from mlte.store.base import StoreType
from mlte.store.custom_list.store import CustomListStore
from mlte.store.custom_list.underlying.fs import FileSystemCustomListStore
from test.store.custom_list.custom_list_store_creators import create_fs_store

DEFAULT_LIST_NAME = "test_list"
DEFAULT_LIST_ENTRIES = [
    {"name": "entry1", "description": "description1"},
    {"name": "entry2", "description": "description2"},
    {"name": "entry3", "description": "description3"},
]
DEFAULT_LIST_ENTRY_NAME = "test entry"
DEFAULT_LIST_ENTRY_DESCRIPTION = "test description"

def custom_list_stores() -> Generator[str, None, None]:
    """
    Yield catalog store fixture names.
    :return: Store fixture name
    """
    # for store_fixture_name in StoreType:
    #     yield store_fixture_name.value
    yield StoreType.LOCAL_FILESYSTEM.value


@pytest.fixture(scope="function")
def create_test_store(tmpdir_factory) -> typing.Callable[[str], CustomListStore]:
    def _make(
        store_fixture_name
    ) -> CustomListStore:
        if store_fixture_name == StoreType.LOCAL_MEMORY.value:
            return create_memory_store()
        elif store_fixture_name == StoreType.LOCAL_FILESYSTEM.value:
            return create_fs_store(tmpdir_factory.mktemp("data"))
        elif store_fixture_name == StoreType.RELATIONAL_DB.value:
            return create_rdbs_store()
        elif store_fixture_name == StoreType.REMOTE_HTTP.value:
            return create_api_and_http_store(catalog_id)
        else:
            raise RuntimeError(
                f"Invalid store type received: {store_fixture_name}"
            )

    return _make


def get_test_list(
    name: str = DEFAULT_LIST_NAME,
    entries: List[str] = DEFAULT_LIST_ENTRIES,
) -> CustomListModel:
    """Helper to get a list structure."""
    return CustomListModel(name=name, entries=entries)

def get_test_entry(
    name: str = DEFAULT_LIST_ENTRY_NAME,
    description: str = DEFAULT_LIST_ENTRY_DESCRIPTION,
) -> CustomListEntryModel:
    """Helper to get a list entry structure."""
    return CustomListEntryModel(name=name, description=description)