"""
test/schema/test_value_schema.py

Unit tests for Value schema.
"""

import pytest

from mlte._private.schema import validate_value_schema
from mlte.api import read_value
from mlte.evidence.metadata import EvidenceMetadata, Identifier
from mlte.value.types.integer import Integer
from mlte.value.types.opaque import Opaque
from mlte.value.types.real import Real


@pytest.mark.skip("Disabled for artifact protocol development.")
def test_real(tmp_path):
    r = Real(
        EvidenceMetadata(
            measurement_type="typename", identifier=Identifier(name="id")
        ),
        3.14,
    )
    r.save()

    d = read_value(f"local://{tmp_path}", "model", "0.0.1", "id")
    validate_value_schema(d)


@pytest.mark.skip("Disabled for artifact protocol development.")
def test_integer(tmp_path):
    r = Integer(
        EvidenceMetadata(
            measurement_type="typename", identifier=Identifier(name="id")
        ),
        3,
    )
    r.save()

    d = read_value(f"local://{tmp_path}", "model", "0.0.1", "id")
    validate_value_schema(d)


@pytest.mark.skip("Disabled for artifact protocol development.")
def test_opaque(tmp_path):
    r = Opaque(
        EvidenceMetadata(
            measurement_type="typename", identifier=Identifier(name="id")
        ),
        {"foo": "bar"},
    )
    r.save()

    d = read_value(f"local://{tmp_path}", "model", "0.0.1", "id")
    validate_value_schema(d)
