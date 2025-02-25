"""
mlte/store/artifact/underlying/rdbs/factory_spec.py

Conversions between schema and internal models.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from mlte._private.fixed_json import json
from mlte.evidence.metadata import EvidenceMetadata
from mlte.spec.model import QACategoryModel, TestSuiteModel
from mlte.store.artifact.underlying.rdbs.metadata import DBArtifactHeader
from mlte.store.artifact.underlying.rdbs.metadata_spec import (
    DBCondition,
    DBEvidenceMetadata,
    DBQACategory,
    DBResult,
    DBSpec,
    DBValidatedSpec,
)
from mlte.store.artifact.underlying.rdbs.reader import DBReader
from mlte.validation.model import ResultModel, TestResultsModel
from mlte.validation.model_condition import ConditionModel

# -------------------------------------------------------------------------
# Spec Factory Methods
# -------------------------------------------------------------------------


def create_spec_db_from_model(
    spec: TestSuiteModel, artifact_header: DBArtifactHeader
) -> DBSpec:
    """Creates the DB object from the corresponding internal model."""
    spec_obj = DBSpec(artifact_header=artifact_header, qa_categories=[])
    for qa_category in spec.qa_categories:
        qa_category_obj = DBQACategory(
            name=qa_category.name,
            description=qa_category.description,
            rationale=qa_category.rationale,
            module=qa_category.module,
            spec=spec_obj,
        )
        spec_obj.qa_categories.append(qa_category_obj)

        for (
            measurement_id,
            condition,
        ) in qa_category.conditions.items():
            condition_obj = DBCondition(
                name=condition.name,
                measurement_id=measurement_id,
                arguments=condition.args_to_json_str(),
                validator=json.dumps(condition.validator.to_json()),
                value_class=condition.value_class,
                qa_category=qa_category_obj,
            )
            qa_category_obj.conditions.append(condition_obj)

    return spec_obj


def create_spec_model_from_db(spec_obj: DBSpec) -> TestSuiteModel:
    """Creates the internal model object from the corresponding DB object."""
    # Creating a Spec from DB data.
    body = TestSuiteModel(
        qa_categories=[
            QACategoryModel(
                name=category.name,
                description=category.description,
                rationale=category.rationale,
                module=category.module,
                conditions={
                    condition.measurement_id: ConditionModel(
                        name=condition.name,
                        validator=json.loads(condition.validator),
                        value_class=condition.value_class,
                        arguments=json.loads(condition.arguments),
                    )
                    for condition in category.conditions
                },
            )
            for category in spec_obj.qa_categories
        ],
    )
    return body


# -------------------------------------------------------------------------
# ValidatedSpec Factory Methods
# -------------------------------------------------------------------------


def create_v_spec_db_from_model(
    validated_spec: TestResultsModel,
    artifact_header: DBArtifactHeader,
    session: Session,
) -> DBValidatedSpec:
    """Creates the DB object from the corresponding internal model."""
    validated_spec_obj = DBValidatedSpec(
        artifact_header=artifact_header,
        results=[],
        spec=(
            DBReader.get_spec(
                validated_spec.test_suite_id,
                artifact_header.version_id,
                session,
            )
            if validated_spec.test_suite_id != ""
            else None
        ),
    )
    for qa_category_name, results in validated_spec.results.items():
        for measurement_id, result in results.items():
            result_obj = DBResult(
                measurement_id=measurement_id,
                type=result.type,
                message=result.message,
                qa_category_id=DBReader.get_qa_category_id(
                    qa_category_name,
                    validated_spec.test_suite_id,
                    artifact_header.version_id,
                    session,
                ),
                validated_spec=validated_spec_obj,
                evidence_metadata=(
                    DBEvidenceMetadata(
                        identifier=measurement_id,
                        measurement_type=result.metadata.measurement_type,
                        info=result.metadata.function,
                    )
                    if result.metadata is not None
                    else None
                ),
            )
            validated_spec_obj.results.append(result_obj)
    return validated_spec_obj


def create_v_spec_model_from_db(
    validated_obj: DBValidatedSpec,
) -> TestResultsModel:
    """Creates the internal model object from the corresponding DB object."""
    body = TestResultsModel(
        results=(
            {
                qa_category.name: {
                    result.measurement_id: ResultModel(
                        type=result.type,
                        message=result.message,
                        measurement_id=EvidenceMetadata(
                            measurement_class=result.evidence_metadata.measurement_type,
                            test_case_id=result.evidence_metadata.identifier,
                        ),
                    )
                    for result in validated_obj.results
                    if result.qa_category.name == qa_category.name
                }
                for qa_category in validated_obj.spec.qa_categories
            }
            if validated_obj.spec is not None
            else {}
        ),
        test_suite_id=(
            validated_obj.spec.artifact_header.identifier
            if validated_obj.spec is not None
            else ""
        ),
        test_suite=(
            create_spec_model_from_db(validated_obj.spec)
            if validated_obj.spec is not None
            else None
        ),
    )
    return body
