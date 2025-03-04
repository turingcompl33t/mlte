"""
Class in charge of validating a TestSuite.
"""

from __future__ import annotations

from mlte.evidence.artifact import Evidence
from mlte.spec.test_suite import TestSuite
from mlte.validation.result import Result
from mlte.validation.test_results import TestResults

# -----------------------------------------------------------------------------
# TestSuiteValidator
# -----------------------------------------------------------------------------


class TestSuiteValidator:
    """
    Helper class to validate a test suite.
    """

    def __init__(self, test_suite: TestSuite):
        """
        Initialize a TestSuiteValidator instance.

        :param test_suite: The test suite to be validated
        """

        self.test_suite = test_suite
        """The specification to be validated."""

        self.evidence: dict[str, Evidence] = {}
        """Where evidence will be gathered for validation."""

    def add_evidence_list(self, evidence_list: list[Evidence]):
        """
        Adds multiple evidence values.

        :param evidence_list: The list of evidence to add to the internal list.
        """
        for evidence in evidence_list:
            self.add_evidence(evidence)

    def add_evidence(self, evidence: Evidence):
        """
        Adds Evidence associated to a test case.

        :param evidence: The evidence to add to the internal list.
        """
        if evidence.metadata.test_case_id in self.evidence:
            raise RuntimeError(
                f"Can't have two values with the same id: {evidence.metadata.test_case_id}"
            )
        self.evidence[evidence.metadata.test_case_id] = evidence

    def validate(self) -> TestResults:
        """
        Validates the internal Evidence given its validators, and generates a TestResults from it.

        :return: The results of the test validation.
        """
        # Check that all test cases have evidence to be validated.
        for test_case_id in self.test_suite.test_cases.keys():
            if test_case_id not in self.evidence:
                raise RuntimeError(
                    f"Test Case '{test_case_id}' does not have evidence that can be validated."
                )

        # Validate and aggregate the results.
        results: dict[str, Result] = {}
        for test_case_id, test_case in self.test_suite.test_cases.items():
            results[test_case_id] = test_case.validate(
                self.evidence[test_case_id]
            )

        return TestResults(test_suite=self.test_suite, results=results)
