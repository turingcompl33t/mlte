"""
mlte/store/catalog/default_catalog.py

MLTE default catalog to come with installation.
"""

from __future__ import annotations

import importlib.resources
import json
import os

import mlte.store.catalog.default as default_entries
from mlte.catalog.model import CatalogEntry
from mlte.store.base import StoreURIPrefix
from mlte.store.catalog.catalog_group import CatalogStoreGroup
from mlte.store.catalog.store import ManagedCatalogSession


class DefaultCatalog:
    """A default catalog with sample code."""

    DEFAULT_CATALOG_ID = "default"
    """Id for default catalog."""

    DEFAULT_STORES_FOLDER = "stores"
    """Default root folder for all built-in stores."""

    @staticmethod
    def add_default_catalog(
        catalog_group: CatalogStoreGroup,
        default_stores_folder: str = DEFAULT_STORES_FOLDER,
    ) -> None:
        """Sets up the default catalog."""
        # The base stores folder has to exist, so create it if it doesn't.
        os.makedirs(f"./{default_stores_folder}", exist_ok=True)
        stores_uri = (
            f"{StoreURIPrefix.LOCAL_FILESYSTEM[0]}{default_stores_folder}"
        )

        # Create the actual default catalog.
        default_catalog_id = DefaultCatalog.DEFAULT_CATALOG_ID
        catalog_group.add_catalog_from_uri(
            id=default_catalog_id, uri=stores_uri, overwite=True
        )

        # Populate it with the default entries, but only the first time.
        with ManagedCatalogSession(
            catalog_group.catalogs[default_catalog_id].session()
        ) as store:
            if len(store.entry_mapper.list()) == 0:
                DefaultCatalog._populate_catalog(
                    catalog_group, default_catalog_id
                )

    @staticmethod
    def _populate_catalog(catalog_group: CatalogStoreGroup, catalog_id: str):
        """Load all entry files from entry folder and put them into default catalog."""
        num_entries = 0
        resources = importlib.resources.files(default_entries)
        with importlib.resources.as_file(resources) as resources_path:
            with os.scandir(resources_path) as files:
                with ManagedCatalogSession(
                    catalog_group.catalogs[catalog_id].session()
                ) as store:
                    print("Loading default catalog entries.")
                    for file in files:
                        if file.is_file() and file.name.endswith("json"):
                            with open(file.path) as open_file:
                                entry = CatalogEntry(**json.load(open_file))
                                store.entry_mapper.create(entry)
                                num_entries += 1
                    print(f"Loaded {num_entries} entries for default catalog.")
