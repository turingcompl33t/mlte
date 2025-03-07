"""
test/store/test_query.py

Unit tests for store query functionality.
"""

from mlte.store.query import (
    AllFilter,
    AndFilter,
    IdentifierFilter,
    NoneFilter,
    OrFilter,
    PropertyFilter,
    Query,
    TagFilter,
    TypeFilter,
)


def test_all() -> None:
    """The all filter can be serialized and deserialized."""
    f = AllFilter()
    assert AllFilter(**f.to_json()) == f


def test_none() -> None:
    """The all filter cna be serialized and deserialized."""
    f = NoneFilter()
    assert NoneFilter(**f.to_json()) == f


def test_identifier() -> None:
    """The identifier filter can be serialized and deserialized."""
    f = IdentifierFilter(id="id0")
    assert IdentifierFilter(**f.to_json()) == f


def test_type() -> None:
    """The type filter can be serialized and deserialized."""
    f = TypeFilter(item_type="test")
    assert TypeFilter(**f.to_json()) == f


def test_tags() -> None:
    """The tag filter can be serialized and deserialized."""
    f = TagFilter(name="test", value="v1")
    assert TagFilter(**f.to_json()) == f


def test_property() -> None:
    """The filter can be serialized and deserialized."""
    f = PropertyFilter(name="test", value="v1")
    assert PropertyFilter(**f.to_json()) == f


def test_and() -> None:
    """The AND filter can be serialized and deserialized."""
    f = AndFilter(
        filters=[
            AllFilter(),
            NoneFilter(),
            IdentifierFilter(id="id0"),
            TypeFilter(item_type="test"),
        ],
    )
    assert AndFilter(**f.to_json()) == f


def test_or() -> None:
    """The OR filter can be serialized and deserialized."""
    f = OrFilter(
        filters=[
            AllFilter(),
            NoneFilter(),
            IdentifierFilter(id="id0"),
            TypeFilter(item_type="test"),
        ],
    )
    assert OrFilter(**f.to_json()) == f


def test_query() -> None:
    """The query can be serialized and deserialized."""
    query = Query()
    print(query.to_json())
    assert Query(**query.to_json()) == query
