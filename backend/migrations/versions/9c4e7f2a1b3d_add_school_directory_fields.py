"""Add official school directory fields.

Revision ID: 9c4e7f2a1b3d
Revises: 7af5b108dd2f
"""

from alembic import op
import sqlalchemy as sa


revision = "9c4e7f2a1b3d"
down_revision = "7af5b108dd2f"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table(
        "schools",
    ) as batch_op:
        batch_op.add_column(
            sa.Column(
                "official_school_code",
                sa.String(length=50),
                nullable=True,
            )
        )

        batch_op.add_column(
            sa.Column(
                "directory_source",
                sa.String(length=20),
                nullable=True,
            )
        )

        batch_op.create_unique_constraint(
            "uq_schools_source_code_name",
            [
                "directory_source",
                "official_school_code",
                "school_name",
            ],
        )


def downgrade():
    with op.batch_alter_table(
        "schools",
    ) as batch_op:
        batch_op.drop_constraint(
            "uq_schools_source_code_name",
            type_="unique",
        )

        batch_op.drop_column(
            "directory_source",
        )

        batch_op.drop_column(
            "official_school_code",
        )
