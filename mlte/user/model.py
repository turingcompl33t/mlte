"""
mlte/user/model.py

Model implementation for a User.
"""

from __future__ import annotations

from typing import List, Optional, Union

from strenum import StrEnum

from mlte.model import BaseModel
from mlte.user import passwords

RESOURCE_ALL_VALUES = "*"
"""Special character used to identify all values of a certain permission."""

# -----------------------------------------------------------------------------
# User model (and sub-models)
# -----------------------------------------------------------------------------


class RoleType(StrEnum):
    """Roles for users."""

    ADMIN = "admin"
    """An admin role, access to everything."""

    REGULAR = "regular"
    """A role with access to artifacts only."""


class BasicUser(BaseModel):
    """A model class representing a user of the system"""

    username: str
    """The username to uniquely identify a user."""

    email: Optional[str] = None
    """An optional email associated to the user."""

    full_name: Optional[str] = None
    """The full name of the user."""

    disabled: bool = False
    """Whether the user is disabled."""

    role: RoleType = RoleType.REGULAR
    """The role associated to the user."""

    groups: List[Group] = []
    """The groups the user is in."""

    def is_equal_to(
        self,
        user: BasicUser,
        only_group_names: bool = True,
        ignore_groups: bool = False,
    ) -> bool:
        """Compares users at the BasicUser level."""
        user1 = BasicUser(**self.to_json())
        user2 = BasicUser(**user.to_json())

        if only_group_names:
            user1.groups = Group.get_group_names(user1.groups)
            user2.groups = Group.get_group_names(user2.groups)

        if ignore_groups:
            user1.groups = []
            user2.groups = []

        return user1 == user2


class User(BasicUser):
    """User with additional information only used locally when stored."""

    hashed_password: str
    """The hashed password of the user."""

    def update_user_data(self, new_user_data: BasicUser) -> User:
        """Update this user, but keeping existing hashed password."""
        hashed_password = self.hashed_password
        updated_user = User(
            **new_user_data.to_json(),
            hashed_password=hashed_password,
        )
        return updated_user


class UserWithPassword(BasicUser):
    """User with additional information only used when creating a user."""

    password: str
    """The plain password of the user."""

    def to_hashed_user(self) -> User:
        """Converts a UserWithPassword model with plain password into a User with a hashed one."""
        # Hash password and create a user with hashed passwords.
        hashed_password = passwords.hash_password(self.password)
        user = User(hashed_password=hashed_password, **self.to_json())
        return user


def update_user_data(
    curr_user: User, new_user_data: Union[UserWithPassword, BasicUser]
) -> User:
    """Get updated user depending on the type, keeping hashed password if no new password is received."""
    if type(new_user_data) is UserWithPassword:
        return new_user_data.to_hashed_user()
    elif type(new_user_data) is BasicUser:
        return curr_user.update_user_data(new_user_data)
    else:
        raise Exception(f"Invalid user type received: {type(new_user_data)}")


# -----------------------------------------------------------------------------
# Group model (and sub-models)
# -----------------------------------------------------------------------------


class MethodType(StrEnum):
    """Types of methods for permissions."""

    GET = "get"
    """Get or read action."""

    POST = "post"
    """Creation action."""

    PUT = "put"
    """Action to edit."""

    DELETE = "delete"
    """Deletion action."""

    ANY = "any"
    """Special action to represent all/any of them."""


class ResourceType(StrEnum):
    """Supported resource types."""

    MODEL = "model"
    """Model and all related artifacts."""

    USER = "user"
    """User resources."""

    GROUP = "group"
    """Group resources."""

    CATALOG = "catalog"
    """Test catalogs."""

    CUSTOM_LIST = "custom_list"
    """Custom lists."""

    @staticmethod
    def get_type_from_url(url: str) -> Optional[ResourceType]:
        """Returns the resource type for the given URL."""
        for resource_type in ResourceType:
            if url.startswith(f"/{resource_type.value}"):
                return resource_type

        # Return none if the URL did not match any known resource type.
        return None


class Group(BaseModel):
    """A user group to which permissions are associated."""

    name: str
    """The name of the group."""

    permissions: List[Permission] = []
    """The permissions associated to the group."""

    @staticmethod
    def get_group_names(groups: List[Group]) -> List[Group]:
        """Given a list of groups, returns a similar list with groups that only contain their names."""
        group_names: List[Group] = []
        for group in groups:
            group_names.append(Group(name=group.name))
        return group_names


class Permission(BaseModel):
    """Permissions for manipulating resources."""

    resource_type: ResourceType
    """The type of resource resource."""

    resource_id: Optional[str] = None
    """The specific resource id to give permissions to, if any."""

    method: MethodType = MethodType.ANY
    """The HTTP method applied on the resource."""

    def to_str(self) -> str:
        """Serialize the permission to a string"""
        serialized = f"{self.resource_type}-{self.method}"
        if self.resource_id is not None:
            serialized = f"{serialized}-{self.resource_id}"
        return serialized

    @staticmethod
    def from_str(permission_str: str) -> Permission:
        """Creates a permission from its string serialization."""
        # Source str can have 2 or 3 parts, depending if resource id was None.
        parts = permission_str.split("-")
        type = parts[0]
        method = parts[1]
        if len(parts) > 2:
            resource_id = parts[2]
        else:
            resource_id = None

        return Permission(
            resource_type=ResourceType(type),
            resource_id=resource_id,
            method=MethodType(method),
        )

    def grants_access(self, request: Permission):
        """Checks if this permission grants access to the recieved request."""
        if self.to_str() == request.to_str():
            # If both are exactly the same, they match.
            return True

        if self.resource_type != request.resource_type:
            # If they point to different resource types, they will never match.
            return False
        else:
            if (
                self.method == request.method
                or self.method == MethodType.ANY
                or request.method == MethodType.ANY
            ):
                # If methods match, or either refer to any method, check resource id.
                if self.resource_id is None:
                    # "None" means all, that means we apply to any request resource id.
                    return True
                elif self.resource_id == request.resource_id:
                    # If the resource ids are the same, we match.
                    return True
                else:
                    # If we have a specific resource id, and they have a different one or "all", we don't match.
                    return False
            else:
                # The methods don't match in some way.
                return False
