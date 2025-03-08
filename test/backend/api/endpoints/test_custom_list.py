"""
test/backend/api/endpoints/test_custom_list.py

Test the API for custom list operations.
"""

import pytest

from typing import Any

from mlte.user.model import UserWithPassword, ResourceType
from test.backend.fixture import user_generator
from test.backend.fixture.test_api import TestAPI
from test.store.custom_list.fixture import get_test_entry, get_entry_uri
from mlte.custom_list.model import CustomListEntryModel, CustomListName
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
    user_generator.get_test_users_with_read_permissions(ResourceType.CUSTOM_LIST),
)
def test_list_lists(
    test_api_fixture, api_user: UserWithPassword
) -> None:
    """Test that lists can be listed."""
    test_api: TestAPI = test_api_fixture(api_user)
    test_client = test_api.get_test_client()
    url = get_entry_uri(only_base=True)
    res = test_client.get(f"{url}")
    assert res.status_code == codes.OK

    collection = res.json()
    assert len(collection) == 2

@pytest.mark.parametrize(
    "api_user",
    user_generator.get_test_users_with_read_permissions(ResourceType.CUSTOM_LIST),
)
def test_list_single_list(
    test_api_fixture, api_user: UserWithPassword
) -> None:
    """Test that a list can be listed."""
    test_api: TestAPI = test_api_fixture(api_user)
    test_client = test_api.get_test_client()
    entry = get_test_entry()

    url = get_entry_uri(custom_list_id=CustomListName.QA_CATEGORIES, no_entry=True)    
    res = test_client.get(f"{url}")
    assert res.status_code == codes.OK

    _ = CustomListEntryModel(**get_entry_using_admin(entry.name, test_api))