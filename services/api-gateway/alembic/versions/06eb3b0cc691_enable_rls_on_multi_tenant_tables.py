"""enable rls on multi-tenant tables

Revision ID: 06eb3b0cc691
Revises: ee7a0c816991
Create Date: 2026-02-07 18:24:45.917111

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '06eb3b0cc691'
down_revision: Union[str, Sequence[str], None] = 'ee7a0c816991'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    tables = [
        "users",
        "proposals",
        "company_asset", 
        "compliance_reports",
        "documents",
    ]

    for table in tables:

        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")

        op.execute(f"""
            CREATE POLICY {table}_tenant_policy
            ON {table}
            USING (tenant_id = current_setting('app.tenant_id')::uuid);
        """)

        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY;")


def downgrade():

    tables = [
        "users",
        "proposals",
        "company_asset",
        "compliance_reports",
        "documents",
    ]

    for table in tables:

        op.execute(f"""
            DROP POLICY IF EXISTS {table}_tenant_policy
            ON {table};
        """)

        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;")