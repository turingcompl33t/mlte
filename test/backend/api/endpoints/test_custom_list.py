"""
test/backend/api/endpoints/test_custom_list.py

Test the API for custom list operations.
"""

import pytest

from typing import Any

from mlte.user.model import UserWithPassword, ResourceType
from test.backend.fixture import user_generator
from test.backend.fixture.test_api import TestAPI
from test.store.custom_list.fixture import get_test_entry
from mlte.backend.core.config import settings
from mlte.custom_list.model import CustomListEntryModel
from mlte.backend.api import codes

CUSTOM_LIST_ENDPOINT = "/custom_list"
CUSTOM_LIST_URI = f"{settings.API_PREFIX}{CUSTOM_LIST_ENDPOINT}"



# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def get_entry_using_admin(entry_id: str, api: TestAPI) -> dict[str, Any]:
    """Gets a custom list entry using admin."""
    return api.admin_read_entity(entry_id, CUSTOM_LIST_URI)

# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------

@pytest.mark.parametrize(
    "api_user",
    user_generator.get_test_users_with_write_permissions(ResourceType.CUSTOM_LIST),
)
def test_create(test_api_fixture, api_user: UserWithPassword) -> None:
    """Test custom list entries can be created."""
    test_api: TestAPI = test_api_fixture(api_user)
    test_client = test_api.get_test_client()
    entry = get_test_entry()

    print(entry)
    print(test_client)

    res = test_client.post(f"{CUSTOM_LIST_URI}", json=entry.to_json())
    print("@@")
    print(res.text)
    assert res.status_code == codes.OK
    _ = CustomListEntryModel(**res.json())

    _ = CustomListEntryModel(**get_entry_using_admin(entry.name, test_api))