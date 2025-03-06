"""
mlte/custom_list/custom_list_names.py

Enum of the predefined custom list names.
"""

from __future__ import annotations

from typing import Any

from strenum import StrEnum


class CustomListName(StrEnum):
    """Custom lists names."""

    QA_CATEGORIES = "qa_categories"
    QUALITY_ATTRIBUTES = "quality_attributes"


class CustomListNameDict(dict[Any, Any]):
    def __setitem__(
        self: "CustomListNameDict",
        key: CustomListName,
        value: CustomListName,
    ):
        if isinstance(key, CustomListName) and isinstance(
            value, CustomListName
        ):
            super().__setitem__(key.value, value.value)
        else:
            raise KeyError(f"CustomListName {key} or {value} is not valid.")

    def __getitem__(self, key):
        if key in CustomListName._value2member_map_:
            return super().__getitem__(key)
        else:
            raise KeyError(f"CustomListName {key} is not valid.")


class CustomListParentMappings:
    parent_mappings = CustomListNameDict()

    parent_mappings[CustomListName.QUALITY_ATTRIBUTES] = (
        CustomListName.QA_CATEGORIES
    )
