"""
test/validation/test_validatedspec.py

Unit tests for ValidatedSpec functionality.
"""

from __future__ import annotations

from typing import Dict, Tuple

import pytest

from mlte.context.context import Context
from mlte.evidence.types.integer import Integer
from mlte.qa_category.costs.storage_cost import StorageCost
from mlte.spec.spec import Spec
from mlte.store.artifact.store import ArtifactStore
from mlte.validation.result import Result
from mlte.validation.spec_validator import TestSuiteValidator
from mlte.validation.test_results import TestResults
from test.store.artifact.fixture import store_with_context  # noqa
from test.value.types.helper import get_sample_evidence_metadata


def test_save_load(store_with_context: Tuple[ArtifactStore, Context]):  # noqa
    store, ctx = store_with_context

    spec = Spec(
        qa_categories={StorageCost("rationale"): {"id": Integer.less_than(3)}}
    )
    specValidator = TestSuiteValidator(spec)

    # A dummy value
    i = Integer(
        get_sample_evidence_metadata(),
        1,
    )
    specValidator.add_value(i)

    validatedSpec = specValidator.validate()
    validatedSpec.save_with(ctx, store)

    r = TestResults.load_with(context=ctx, store=store)
    assert r == validatedSpec


def test_no_result_and_no_qa_category():
    # Spec does not have Result for condition, not even a qa category.
    spec = Spec(
        qa_categories={StorageCost("rationale"): {"test": Integer.less_than(3)}}
    )

    results: Dict[str, Dict[str, Result]] = {}
    with pytest.raises(RuntimeError):
        _ = TestResults(test_suite=spec, results=results)


def test_no_result():
    # Spec does not have Result for condition.
    spec = Spec(
        qa_categories={StorageCost("rationale"): {"test": Integer.less_than(3)}}
    )

    results: Dict[str, Dict[str, Result]] = {"StorageCost": {}}
    with pytest.raises(RuntimeError):
        _ = TestResults(test_suite=spec, results=results)
