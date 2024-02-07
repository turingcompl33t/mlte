"""
mlte/store/artifact/underlying/rdbs/metadata_nc.py

Definition of the metadata (DB schema) for negotiation card and report elements in the artifact store.
"""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy import ForeignKey, select
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from mlte.model.shared import DataClassification, ProblemType
from mlte.store.artifact.underlying.rdbs.metadata import (
    DBArtifactHeader,
    DBBase,
)

# -------------------------------------------------------------------------
# Negotiation Card
# -------------------------------------------------------------------------


class DBNegotiationCard(DBBase):
    __tablename__ = "negotiation_card"

    # General
    id: Mapped[int] = mapped_column(primary_key=True)
    artifact_header_id: Mapped[DBArtifactHeader] = mapped_column(
        ForeignKey("artifact_header.id")
    )
    artifact_header: Mapped[DBArtifactHeader] = relationship(
        back_populates="body_negotiation_card"
    )

    # System
    sys_goals: Mapped[List[DBGoalDescriptor]] = relationship()
    sys_problem_type_id: Mapped[int] = mapped_column(
        ForeignKey("nc_problem_type.id")
    )
    sys_problem_type: Mapped[DBProblemType] = relationship()
    sys_task: Mapped[Optional[str]]
    sys_usage_context: Mapped[Optional[str]]
    sys_risks_fp: Mapped[Optional[str]]
    sys_risks_fn: Mapped[Optional[str]]
    sys_risks_other: Mapped[Optional[str]]

    # Data
    data_descriptors: Mapped[List[DBDataDescriptor]] = relationship()

    # Model
    model_dev_resources_id: Mapped[int] = mapped_column(
        ForeignKey("nc_model_resource.id")
    )
    model_dev_resources: Mapped[DBModelResourcesDescriptor] = relationship(
        foreign_keys=[model_dev_resources_id]
    )
    model_prod_integration: Mapped[Optional[str]]
    model_prod_interface_input_desc: Mapped[Optional[str]]
    model_prod_interface_output_desc: Mapped[Optional[str]]
    model_prod_resources_id: Mapped[int] = mapped_column(
        ForeignKey("nc_model_resource.id")
    )
    model_prod_resources: Mapped[DBModelResourcesDescriptor] = relationship(
        foreign_keys=[model_prod_resources_id]
    )

    def __repr__(self) -> str:
        return f"NegotiationCard(id={self.id!r}, artifact_header={self.artifact_header!r})"


# -------------------------------------------------------------------------
# Report
# -------------------------------------------------------------------------


# -------------------------------------------------------------------------
# Shared Elements
# -------------------------------------------------------------------------


class DBGoalDescriptor(DBBase):
    __tablename__ = "nc_goal_descriptor"

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[Optional[str]]
    negotiation_card_id: Mapped[int] = mapped_column(
        ForeignKey("negotiation_card.id")
    )

    metrics: Mapped[List[DBMerticDescriptor]] = relationship(
        back_populates="goal_descriptor"
    )

    def __repr__(self) -> str:
        return f"GoalDescriptor(id={self.id!r}, name={self.description!r})"


class DBMerticDescriptor(DBBase):
    __tablename__ = "nc_metric_descriptor"

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[Optional[str]]
    baseline: Mapped[Optional[str]]
    goal_descriptor_id: Mapped[int] = mapped_column(
        ForeignKey("nc_goal_descriptor.id")
    )

    goal_descriptor: Mapped[DBGoalDescriptor] = relationship(
        back_populates="metrics"
    )

    def __repr__(self) -> str:
        return f"MetricDescriptor(id={self.id!r}, name={self.description!r}, baseline={self.baseline!r})"


class DBProblemType(DBBase):
    __tablename__ = "nc_problem_type"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    def __repr__(self) -> str:
        return f"ProblemType(id={self.id!r}, name={self.name!r})"


class DBDataDescriptor(DBBase):
    __tablename__ = "nc_data_descriptor"

    id: Mapped[int] = mapped_column(primary_key=True)

    description: Mapped[Optional[str]]
    source: Mapped[Optional[str]]
    access: Mapped[Optional[str]]
    rights: Mapped[Optional[str]]
    policies: Mapped[Optional[str]]
    identifiable_information: Mapped[Optional[str]]
    classification_id: Mapped[int] = mapped_column(
        ForeignKey("nc_data_classification.id")
    )
    negotiation_card_id: Mapped[int] = mapped_column(
        ForeignKey("negotiation_card.id")
    )

    classification: Mapped[DBDataClassification] = relationship()
    labels: Mapped[List[DBLabelDescriptor]] = relationship(
        back_populates="data_descriptor"
    )
    fields: Mapped[List[DBFieldDescriptor]] = relationship(
        back_populates="data_descriptor"
    )

    def __repr__(self) -> str:
        return f"DataDescriptor(id={self.id!r}, description={self.description!r}, source={self.source!r}, access={self.access!r}, rights={self.rights!r}, policies={self.policies!r}, identifiable_information={self.identifiable_information!r})"


class DBDataClassification(DBBase):
    __tablename__ = "nc_data_classification"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    def __repr__(self) -> str:
        return f"DataClassification(id={self.id!r}, name={self.name!r})"


class DBLabelDescriptor(DBBase):
    __tablename__ = "nc_label_descriptor"

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[Optional[str]]
    percentage: Mapped[Optional[float]]
    data_descriptor_id: Mapped[int] = mapped_column(
        ForeignKey("nc_data_descriptor.id")
    )

    data_descriptor: Mapped[DBDataDescriptor] = relationship(
        back_populates="labels"
    )

    def __repr__(self) -> str:
        return f"LabelDescriptor(id={self.id!r}, description={self.description!r}, description={self.percentage!r})"


class DBFieldDescriptor(DBBase):
    __tablename__ = "nc_field_descriptor"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[Optional[str]]
    description: Mapped[Optional[str]]
    type: Mapped[Optional[str]]
    expected_values: Mapped[Optional[str]]
    missing_values: Mapped[Optional[str]]
    special_values: Mapped[Optional[str]]
    data_descriptor_id: Mapped[int] = mapped_column(
        ForeignKey("nc_data_descriptor.id")
    )

    data_descriptor: Mapped[DBDataDescriptor] = relationship(
        back_populates="fields"
    )

    def __repr__(self) -> str:
        return f"LabelDescriptor(id={self.id!r}, name={self.name!r}, description={self.description!r}, type={self.type!r}, expected_values={self.expected_values!r}, missing_values={self.missing_values!r}, special_values={self.special_values!r})"


class DBModelResourcesDescriptor(DBBase):
    __tablename__ = "nc_model_resource"

    id: Mapped[int] = mapped_column(primary_key=True)
    cpu: Mapped[Optional[str]]
    gpu: Mapped[Optional[str]]
    memory: Mapped[Optional[str]]
    storage: Mapped[Optional[str]]
    negotiation_card_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("negotiation_card.id")
    )

    def __repr__(self) -> str:
        return f"ModelResourcesDescriptor(id={self.id!r}, cpu={self.cpu!r}, gpu={self.gpu!r}, memory={self.memory!r}, storage={self.storage!r})"


# -------------------------------------------------------------------------
# Pre-filled table functions.
# -------------------------------------------------------------------------


def init_problem_types(session: Session):
    """Initializes the table with the configured problem types."""
    if session.scalars(select(DBProblemType)).first() is None:
        types = [e.value for e in DataClassification]
        for type in types:
            type_obj = DBProblemType(name=type)
            session.add(type_obj)
        session.commit()


def init_classification_types(session: Session):
    """Initializes the table with the configured classification types."""
    if session.scalars(select(DBDataClassification)).first() is None:
        types = [e.value for e in ProblemType]
        for type in types:
            type_obj = DBDataClassification(name=type)
            session.add(type_obj)
        session.commit()
