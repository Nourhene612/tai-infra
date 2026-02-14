"""convert login_attempts PK to UUID

Revision ID: b2f7c9a1e6d4
Revises: 04aaa59094df
Create Date: 2026-02-05 22:30:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b2f7c9a1e6d4'
down_revision = 'remove_api_keys'
branch_labels = None
depend_on = None


def upgrade() -> None:
    # 1) add new UUID column with default
    op.add_column('login_attempts', sa.Column('id_new', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=True))

    # 2) populate existing rows with UUIDs
    op.execute("UPDATE login_attempts SET id_new = gen_random_uuid() WHERE id_new IS NULL;")

    # 3) drop existing primary key constraint
    op.drop_constraint('login_attempts_pkey', 'login_attempts', type_='primary')

    # 4) create new primary key on id_new
    op.create_primary_key('login_attempts_pkey', 'login_attempts', ['id_new'])

    # 5) drop old id column
    op.drop_column('login_attempts', 'id')

    # 6) rename id_new -> id
    op.alter_column('login_attempts', 'id_new', new_column_name='id')

    # 7) ensure server_default remains for future inserts
    op.alter_column('login_attempts', 'id', server_default=sa.text('gen_random_uuid()'))


def downgrade() -> None:
    # Reverse: add old bigint id, populate sequentially, set as pk, drop uuid id
    op.add_column('login_attempts', sa.Column('old_id', sa.BigInteger(), autoincrement=True, nullable=True))

    # populate old_id with sequence numbers
    op.execute("WITH seq AS (SELECT id_new, row_number() OVER () AS rn FROM login_attempts) UPDATE login_attempts SET old_id = seq.rn FROM seq WHERE login_attempts.id = seq.id_new;")

    # drop current pk
    op.drop_constraint('login_attempts_pkey', 'login_attempts', type_='primary')

    # create primary key on old_id
    op.create_primary_key('login_attempts_pkey', 'login_attempts', ['old_id'])

    # drop uuid id column
    op.drop_column('login_attempts', 'id')

    # rename old_id -> id
    op.alter_column('login_attempts', 'old_id', new_column_name='id')

    # restore autoincrement behaviour if needed (left as simple bigint primary key)
    
