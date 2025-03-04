"""
Unit tests for TestSuiteValidator functionality.
"""

from __future__ import annotations

import pytest

from mlte.evidence.types.integer import Integer
from mlte.spec.test_case import TestCase
from mlte.spec.test_suite import TestSuite
from mlte.validation.test_suite_validator import TestSuiteValidator
from test.evidence.types.helper import get_sample_evidence_metadata
from test.fixture.artifact import make_complete_test_suite_model


def test_no_requirement():
    # Test Sute Validator does not have value for evidence.
    test_suite = TestSuite.from_model(make_complete_test_suite_model())
    test_suite_validator = TestSuiteValidator(test_suite)

    i = Integer(1).with_metadata(get_sample_evidence_metadata())
    test_suite_validator.add_evidence(i)

    with pytest.raises(RuntimeError):
        _ = test_suite_validator.validate()


def test_success():
    test_suite = TestSuite(
        test_cases={
            test_case.identifier: TestCase.from_model(test_case)
            for test_case in make_complete_test_suite_model().test_cases
        }
    )
    test_suite_validator = TestSuiteValidator(test_suite)

    m = get_sample_evidence_metadata(test_case_id="Test1")

    i = Integer(1).with_metadata(m)
    test_suite_validator.add_evidence(i)

    test_results = test_suite_validator.validate()
    assert test_results is not None
