"""Remove api_keys table

Revision ID: remove_api_keys
Revises: 04aaa59094df
Create Date: 2026-02-05 22:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'remove_api_keys'
down_revision: Union[str, Sequence[str], None] = '04aaa59094df'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove api_keys table."""
    # Use IF EXISTS to avoid failing if the table is already absent
    op.execute("DROP TABLE IF EXISTS api_keys CASCADE;")


def downgrade() -> None:
    """Recreate api_keys table."""
    op.create_table('api_keys',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('key', sa.VARCHAR(length=255), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
