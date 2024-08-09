"""
mlte/store/user/store.py

MLTE user store interface implementation.
"""

from __future__ import annotations

from typing import List, Union, cast

from mlte.store.base import ManagedSession, ResourceMapper, StoreSession
from mlte.store.common.query import Query
from mlte.user.model import (
    BasicUser,
    Group,
    Permission,
    ResourceType,
    User,
    UserWithPassword,
)

# -----------------------------------------------------------------------------
# UserStoreSession
# -----------------------------------------------------------------------------


class UserStoreSession(StoreSession):
    """The base class for all implementations of the MLTE user store session."""

    ID_MAP = {
        ResourceType.USER: "username",
        ResourceType.MODEL: "identifier",
        ResourceType.GROUP: "name",
    }
    """Map of ids used for each resource."""

    def __init__(self):
        self.user_mapper = UserMapper()
        """Mapper for the user resource."""

        self.group_mapper = GroupMapper()
        """Mapper for the group resource."""

        self.permission_mapper = PermissionMapper()
        """Mapper for the permission resource."""


class ManagedUserSession(ManagedSession):
    """A simple context manager for store sessions."""

    def __enter__(self) -> UserStoreSession:
        return cast(UserStoreSession, self.session)


class UserMapper(ResourceMapper):
    """A interface for mapping CRUD actions to store users."""

    def create(self, new_user: UserWithPassword) -> User:
        raise NotImplementedError(self.NOT_IMPLEMENTED_ERROR_MSG)

    def edit(self, updated_user: Union[UserWithPassword, BasicUser]) -> User:
        raise NotImplementedError(self.NOT_IMPLEMENTED_ERROR_MSG)

    def read(self, user_id: str) -> User:
        raise NotImplementedError(self.NOT_IMPLEMENTED_ERROR_MSG)

    def list(self) -> List[str]:
        raise NotImplementedError(self.NOT_IMPLEMENTED_ERROR_MSG)

    def delete(self, user_id: str) -> User:
        raise NotImplementedError(self.NOT_IMPLEMENTED_ERROR_MSG)


class GroupMapper(ResourceMapper):
    """A interface for mapping CRUD actions to store groups."""

    def create(self, new_group: Group) -> Group:
        raise NotImplementedError(self.NOT_IMPLEMENTED_ERROR_MSG)

    def edit(self, updated_group: Group) -> Group:
        raise NotImplementedError(self.NOT_IMPLEMENTED_ERROR_MSG)

    def read(self, group_id: str) -> Group:
        raise NotImplementedError(self.NOT_IMPLEMENTED_ERROR_MSG)

    def list(self) -> List[str]:
        raise NotImplementedError(self.NOT_IMPLEMENTED_ERROR_MSG)

    def delete(self, group_id: str) -> Group:
        raise NotImplementedError(self.NOT_IMPLEMENTED_ERROR_MSG)


class PermissionMapper(ResourceMapper):
    """A interface for mapping CRUD actions to store permissions."""

    def create(self, new_permission: Permission) -> Permission:
        raise NotImplementedError(self.NOT_IMPLEMENTED_ERROR_MSG)

    def edit(self, updated_permission: Permission) -> Permission:
        raise NotImplementedError(self.NOT_IMPLEMENTED_ERROR_MSG)

    def read(self, permission: str) -> Permission:
        raise NotImplementedError(self.NOT_IMPLEMENTED_ERROR_MSG)

    def list(self) -> List[str]:
        raise NotImplementedError(self.NOT_IMPLEMENTED_ERROR_MSG)

    def delete(self, permission: str) -> Permission:
        raise NotImplementedError(self.NOT_IMPLEMENTED_ERROR_MSG)

    def list_details(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Permission]:
        entry_ids = self.list()
        return [self.read(entry_id) for entry_id in entry_ids][
            offset : offset + limit
        ]

    def search(
        self,
        query: Query = Query(),
    ) -> List[Permission]:
        # TODO: not the most efficient way, since it loads all items first, before filtering.
        entries = self.list_details()
        return [entry for entry in entries if query.filter.match(entry)]
