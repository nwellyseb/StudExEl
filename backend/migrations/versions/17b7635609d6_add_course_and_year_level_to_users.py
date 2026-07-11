"""Add course and year level to users

Revision ID: 17b7635609d6
Revises:
Create Date: 2026-07-11 12:33:08.207254
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "17b7635609d6"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users") as batch_op:

        batch_op.add_column(
            sa.Column(
                "course",
                sa.String(length=100),
                nullable=True
            )
        )

        batch_op.add_column(
            sa.Column(
                "year_level",
                sa.String(length=30),
                nullable=True
            )
        )


def downgrade():
    with op.batch_alter_table("users") as batch_op:

        batch_op.drop_column("year_level")

        batch_op.drop_column("course")