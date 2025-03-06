"""
mlte/backend/core/state.py

Globally-accessible application state.
"""

from __future__ import annotations

from typing import Optional

from mlte.store.artifact.store import ArtifactStore
from mlte.store.catalog.catalog_group import CatalogStoreGroup
from mlte.store.catalog.store import CatalogStore
from mlte.store.custom_list.store import CustomListStore
from mlte.store.user.store import UserStore


class State:
    """Global state object."""

    def __init__(self):
        self.reset()

    def reset(self):
        """Resets all internal state to defaults."""
        self._artifact_store: Optional[ArtifactStore] = None
        """The artifact store instance maintained by the state object."""

        self._user_store: Optional[UserStore] = None
        """The user store instance maintained by the state object."""

        self._catalog_stores: CatalogStoreGroup = CatalogStoreGroup()
        """The list of catalog store instances maintained by the state object."""

        self._custom_list_store: Optional[CustomListStore] = None
        """The custom list store instance maintained by the state object."""

        self._jwt_secret_key: str = ""
        """Secret key used to sign authentication tokens."""

    def set_artifact_store(self, store: ArtifactStore):
        """Set the globally-configured backend artifact store."""
        self._artifact_store = store

    def set_user_store(self, store: UserStore):
        """Set the globally-configured backend user store."""
        self._user_store = store

    def add_catalog_store(
        self, store: CatalogStore, id: str, overwite: bool = False
    ):
        """Adds to the the globally-configured backend list of catalog stores."""
        self._catalog_stores.add_catalog(id, store, overwite)

    def add_catalog_store_from_uri(
        self, store_uri: str, id: str, overwite: bool = False
    ):
        """Adds to the the globally-configured backend list of catalog stores."""
        self._catalog_stores.add_catalog_from_uri(id, store_uri, overwite)

    def set_custom_list_store(self, store: CustomListStore):
        """Set the globally-configured backend custom list store."""
        self._custom_list_store = store

    def set_token_key(self, token_key: str):
        """Sets the globally used token secret key."""
        self._jwt_secret_key = token_key

    @property
    def artifact_store(self) -> ArtifactStore:
        """Get the globally-configured backend artifact store."""
        if self._artifact_store is None:
            raise RuntimeError("Artifact store is not configured.")
        return self._artifact_store

    @property
    def user_store(self) -> UserStore:
        """Get the globally-configured backend user store."""
        if self._user_store is None:
            raise RuntimeError("User store is not configured.")
        return self._user_store

    @property
    def catalog_stores(self) -> CatalogStoreGroup:
        """Get the globally-configured backend catalog store group."""
        return self._catalog_stores

    @property
    def token_key(self) -> str:
        """Get the globally-configured token secret key."""
        if self._jwt_secret_key == "":
            raise RuntimeError("Token key has not been configured.")
        return self._jwt_secret_key

    @property
    def custom_list_store(self) -> CustomListStore:
        """Get the globablly-configured backend custom list store."""
        if self._custom_list_store is None:
            raise RuntimeError("Custom list store is not configured.")
        return self._custom_list_store


# Globally-accessible application state
state = State()
