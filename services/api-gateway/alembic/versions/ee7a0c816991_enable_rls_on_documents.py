"""enable rls on documents

Revision ID: ee7a0c816991
Revises: b2f7c9a1e6d4
Create Date: 2026-02-07 16:55:06.965534

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ee7a0c816991'
down_revision: Union[str, Sequence[str], None] = 'b2f7c9a1e6d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
   
    
    op.execute("""
        ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
    """)

    op.execute("""
        CREATE POLICY tenant_isolation_policy
        ON documents
        USING (tenant_id = current_setting('app.tenant_id')::uuid);
    """)

    op.execute("""
        CREATE POLICY insert_tenant_check
        ON documents
        FOR INSERT
        WITH CHECK (tenant_id = current_setting('app.tenant_id')::uuid);
    """)

    op.execute("""
        CREATE POLICY owner_update_policy
        ON documents
        FOR UPDATE
        USING (created_by = current_setting('app.user_id')::uuid);
    """)

    op.execute("""
        CREATE POLICY owner_delete_policy
        ON documents
        FOR DELETE
        USING (created_by = current_setting('app.user_id')::uuid);
    """)

    op.execute("""
        ALTER TABLE documents FORCE ROW LEVEL SECURITY;
    """)

def downgrade() :
    op.execute("""
        DROP POLICY IF EXISTS tenant_isolation_policy ON documents;
    """)

    op.execute("""
        DROP POLICY IF EXISTS insert_tenant_check ON documents;
    """)

    op.execute("""
        DROP POLICY IF EXISTS owner_update_policy ON documents;
    """)

    op.execute("""
        DROP POLICY IF EXISTS owner_delete_policy ON documents;
    """)

    op.execute("""
        ALTER TABLE documents DISABLE ROW LEVEL SECURITY;
    """)
