"""init terms

Revision ID: 0001_init_terms
Revises: 
Create Date: 2025-10-17 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0001_init_terms"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "terms",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("keyword", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_terms_id", "terms", ["id"], unique=False)
    op.create_index("ix_terms_keyword", "terms", ["keyword"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_terms_keyword", table_name="terms")
    op.drop_index("ix_terms_id", table_name="terms")
    op.drop_table("terms")


