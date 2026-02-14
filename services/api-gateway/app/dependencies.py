"""
FastAPI dependencies for database sessions and RLS context
"""
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Generator
from uuid import UUID

from app.db.session import SessionLocal
from app.db.rls import set_rls_context


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency to get a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user_id(request: Request) -> UUID:
    """
    Extract current user ID from request context.
    TODO: Implement proper JWT/auth extraction
    
    For now, expects X-User-ID header.
    """
    user_id = request.headers.get("X-User-ID")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-User-ID header"
        )
    try:
        return UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid X-User-ID format"
        )


def get_current_tenant_id(request: Request) -> UUID:
    """
    Extract current tenant ID from request context.
    TODO: Implement proper JWT/auth extraction
    
    For now, expects X-Tenant-ID header.
    """
    tenant_id = request.headers.get("X-Tenant-ID")
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Tenant-ID header"
        )
    try:
        return UUID(tenant_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid X-Tenant-ID format"
        )


def get_db_with_rls(
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id),
    tenant_id: UUID = Depends(get_current_tenant_id),
) -> Session:
    """
    FastAPI dependency to get a database session with RLS context initialized.
    
    Usage in endpoints:
        @app.get("/documents/")
        async def list_documents(session: Session = Depends(get_db_with_rls)):
            # RLS context is already set
            return session.query(Document).all()
    """
    set_rls_context(db, tenant_id, user_id)
    return db
