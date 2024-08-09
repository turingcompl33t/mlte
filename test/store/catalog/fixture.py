"""
test/store/catalog/fixture.py

Fixtures for MLTE catalog store unit tests.
"""

from __future__ import annotations

import typing
from pathlib import Path
from typing import Generator, Optional

import pytest
from sqlalchemy import StaticPool

from mlte.store.base import StoreURI, StoreURIPrefix
from mlte.store.catalog.factory import create_store
from mlte.store.catalog.store import CatalogStore
from mlte.store.catalog.underlying.fs import FileSystemCatalogStore
from mlte.store.catalog.underlying.memory import InMemoryCatalogStore
from mlte.store.catalog.underlying.rdbs.store import RelationalDBCatalogStore

CACHED_DEFAULT_MEMORY_STORE: Optional[InMemoryCatalogStore] = None
"""Global, initial, in memory store, cached for faster testing."""

_STORE_FIXTURE_NAMES = ["memory_store", "fs_store", "rdbs_store"]


def catalog_stores() -> Generator[str, None, None]:
    """
    Yield catalog store fixture names.
    :return: Store fixture name
    """
    for store_fixture_name in _STORE_FIXTURE_NAMES:
        yield store_fixture_name


def create_memory_store() -> InMemoryCatalogStore:
    """Returns an in-memory store. Caches an initialized one to make testing faster."""
    global CACHED_DEFAULT_MEMORY_STORE
    if CACHED_DEFAULT_MEMORY_STORE is None:
        CACHED_DEFAULT_MEMORY_STORE = typing.cast(
            InMemoryCatalogStore, create_store(StoreURIPrefix.LOCAL_MEMORY[0])
        )

    return CACHED_DEFAULT_MEMORY_STORE.clone()


def create_fs_store(tmp_path: Path) -> FileSystemCatalogStore:
    """Creates a file system store."""
    return typing.cast(
        FileSystemCatalogStore,
        create_store(f"{StoreURIPrefix.LOCAL_FILESYSTEM[1]}{tmp_path}"),
    )


def create_rdbs_store() -> RelationalDBCatalogStore:
    IN_MEMORY_SQLITE_DB = "sqlite+pysqlite:///:memory:"
    return RelationalDBCatalogStore(
        StoreURI.from_string(IN_MEMORY_SQLITE_DB),
        poolclass=StaticPool,
    )


@pytest.fixture(scope="function")
def create_test_store(tmpdir_factory) -> typing.Callable[[str], CatalogStore]:
    def _make(store_fixture_name) -> CatalogStore:
        if store_fixture_name == "memory_store":
            return create_memory_store()
        elif store_fixture_name == "fs_store":
            return create_fs_store(tmpdir_factory.mktemp("data"))
        else:
            return create_rdbs_store()

    return _make
