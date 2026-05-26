"""add_indexes

Revision ID: add_indexes
Revises: add_categories
Create Date: 2026-05-26

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import inspect


revision: str = "add_indexes"
down_revision: Union[str, Sequence[str], None] = "add_categories"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _index_names(conn, table_name: str) -> set[str]:
    return {idx["name"] for idx in inspect(conn).get_indexes(table_name)}


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)
    tables = set(inspector.get_table_names())

    if "records" in tables:
        existing = _index_names(conn, "records")
        if "ix_records_user_id_created_at" not in existing:
            op.create_index(
                "ix_records_user_id_created_at",
                "records",
                ["user_id", "created_at"],
                unique=False,
            )

    if "materials" in tables:
        existing = _index_names(conn, "materials")
        if "ix_materials_category" not in existing:
            op.create_index(
                op.f("ix_materials_category"),
                "materials",
                ["category"],
                unique=False,
            )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)
    tables = set(inspector.get_table_names())

    if "materials" in tables:
        existing = _index_names(conn, "materials")
        if "ix_materials_category" in existing:
            op.drop_index(op.f("ix_materials_category"), table_name="materials")

    if "records" in tables:
        existing = _index_names(conn, "records")
        if "ix_records_user_id_created_at" in existing:
            op.drop_index("ix_records_user_id_created_at", table_name="records")
