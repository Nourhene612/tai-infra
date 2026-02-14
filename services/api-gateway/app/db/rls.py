"""
RLS (Row Level Security) Context Management
Configures PostgreSQL application settings for tenant and user isolation
"""
from sqlalchemy import text
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Union


def set_rls_context(
    session: Session,
    tenant_id: Union[UUID, str],
    user_id: Union[UUID, str],
) -> None:
    """
    Set PostgreSQL application settings for RLS policies.
    Must be called before database operations for RLS to work.
    
    Args:
        session: SQLAlchemy sync session
        tenant_id: UUID of the tenant
        user_id: UUID of the user
    """
    tenant_id_str = str(tenant_id) if isinstance(tenant_id, UUID) else tenant_id
    user_id_str = str(user_id) if isinstance(user_id, UUID) else user_id
    
    # Set tenant context
    session.execute(
        text("SELECT set_config('app.tenant_id', :tid, true)"),
        {"tid": tenant_id_str},
    )
    
    # Set user context
    session.execute(
        text("SELECT set_config('app.user_id', :uid, true)"),
        {"uid": user_id_str},
    )


def clear_rls_context(session: Session) -> None:
    """
    Clear RLS context from PostgreSQL session settings.
    """
    session.execute(text("SELECT set_config('app.tenant_id', NULL, true)"))
    session.execute(text("SELECT set_config('app.user_id', NULL, true)"))
