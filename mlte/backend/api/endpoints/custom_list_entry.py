"""
mlte/backend/api/endpoints/custom_list.py

Custom list Entry CRUD endpoints.
"""

from fastapi import APIRouter, HTTPException

import mlte.backend.api.codes as codes
import mlte.store.error as errors
from mlte.backend.api.auth.authorization import AuthorizedUser
from mlte.backend.api.error_handlers import raise_http_internal_error
from mlte.backend.core import state_stores
from mlte.custom_list.custom_list_names import CustomListName
from mlte.custom_list.model import CustomListEntryModel

router = APIRouter()


@router.post("/{custom_list_id}/entry")
def create_custom_list_entry(
    *,
    custom_list_id: CustomListName,
    entry: CustomListEntryModel,
    current_user: AuthorizedUser,
) -> CustomListEntryModel:
    """
    Create a custom list entry.
    :param entry: The custom list entry to create
    :return: The created custom list entry
    """
    with state_stores.custom_list_stores_session() as custom_list_store:
        try:
            return custom_list_store.custom_list_entry_mapper.create(
                entry, custom_list_id
            )
        except errors.ErrorNotFound as e:
            raise HTTPException(status_code=codes.NOT_FOUND, detail=f"{e}")
        except errors.ErrorAlreadyExists as e:
            raise HTTPException(
                status_code=codes.ALREADY_EXISTS, detail=f"Exists: {e}"
            )
        except Exception as e:
            raise_http_internal_error(e)


@router.get("/{custom_list_id}/entry/{custom_list_entry_id}")
def read_custom_list_entry(
    *,
    custom_list_id: CustomListName,
    entry_id: str,
    current_user: AuthorizedUser,
) -> CustomListEntryModel:
    """
    Read a custom list Entry.
    :param entry_id: The entry id to read
    :return: The read entry
    """
    with state_stores.custom_list_stores_session() as custom_list_store:
        try:
            return custom_list_store.custom_list_entry_mapper.read(
                entry_id, custom_list_id
            )
        except errors.ErrorNotFound as e:
            raise HTTPException(status_code=codes.NOT_FOUND, detail=f"{e}")
        except errors.ErrorNotFound as e:
            raise HTTPException(
                status_code=codes.NOT_FOUND, detail=f"{e} not found."
            )
        except Exception as e:
            raise_http_internal_error(e)


@router.put("/{custom_list_id}/entry")
def edit_custom_list_entry(
    *,
    custom_list_id: CustomListName,
    entry: CustomListEntryModel,
    current_user: AuthorizedUser,
) -> CustomListEntryModel:
    """
    Edit a custom list entry.
    :param entry: The custom list entry to edit
    :return: The edited custom list entry
    """
    with state_stores.custom_list_stores_session() as custom_list_store:
        try:
            return custom_list_store.custom_list_entry_mapper.edit(
                entry, custom_list_id
            )
        except errors.ErrorNotFound as e:
            raise HTTPException(status_code=codes.NOT_FOUND, detail=f"{e}")
        except Exception as e:
            raise_http_internal_error(e)


@router.delete("/{custom_list_id}/entry/{custom_list_entry_id}")
def delete_custom_list_entry(
    *,
    custom_list_id: CustomListName,
    entry_id: str,
    current_user: AuthorizedUser,
) -> CustomListEntryModel:
    """
    Delete a custom list Entry.
    :param entry_id: The entry id to delete
    :return: The deleted entry
    """
    with state_stores.custom_list_stores_session() as custom_list_store:
        try:
            return custom_list_store.custom_list_entry_mapper.delete(
                entry_id, custom_list_id
            )
        except errors.ErrorNotFound as e:
            raise HTTPException(
                status_code=codes.NOT_FOUND, detail=f"{e} not found."
            )
        except Exception as e:
            raise_http_internal_error(e)
