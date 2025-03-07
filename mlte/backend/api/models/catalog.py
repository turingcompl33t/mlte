"""
mlte/backend/api/models/catalog_model.py

Catalog data.
"""

from mlte.model.base_model import BaseModel


class CatalogReply(BaseModel):
    id: str
    """The catalog idenditifier."""

    read_only: bool
    """Whether the catalog is read only or not."""

    type: str
    """Type of catalog."""
