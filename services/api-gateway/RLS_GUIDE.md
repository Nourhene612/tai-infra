# PostgreSQL RLS (Row Level Security) Implementation Guide

## Overview
RLS has been enabled on multi-tenant tables (`documents`, `users`, `proposals`, `company_asset`, `compliance_reports`) to prevent data leakage between tenants.

## Database Migrations
- ✅ Migration `ee7a0c816991`: RLS policies for `documents` table
- ✅ Migration `06eb3b0cc691`: RLS policies for multi-tenant tables

## How RLS Works

RLS uses PostgreSQL application settings to control row visibility:
- `app.tenant_id` - Controls which tenant's data is visible
- `app.user_id` - Controls owner-level permissions (documents: UPDATE/DELETE only by creator)

### Policies Applied

**Documents table (ee7a0c816991):**
- `tenant_isolation_policy` (SELECT): `tenant_id = current_setting('app.tenant_id')::uuid`
- `insert_tenant_check` (INSERT): `tenant_id = current_setting('app.tenant_id')::uuid`
- `owner_update_policy` (UPDATE): `created_by = current_setting('app.user_id')::uuid`
- `owner_delete_policy` (DELETE): `created_by = current_setting('app.user_id')::uuid`

**Multi-tenant tables (06eb3b0cc691):**
- `{table}_tenant_policy` (SELECT): `tenant_id = current_setting('app.tenant_id')::uuid`
- Note: INSERT/UPDATE/DELETE policies needed per use case

## Integration Steps

### 1. Update FastAPI Middleware (REQUIRED)
The middleware in `app/main.py` needs to extract tenant_id and user_id from JWT tokens:

```python
from fastapi import Request
from app.dependencies import get_current_user_id, get_current_tenant_id
from app.db.rls import set_rls_context
from app.db.session import SessionLocal

@app.middleware("http")
async def rls_context_middleware(request: Request, call_next):
    """Extract auth context and set RLS"""
    # Example from JWT token:
    # token = request.headers.get("Authorization", "").replace("Bearer ", "")
    # claims = decode_jwt_token(token)
    # tenant_id = claims.get("tenant_id")
    # user_id = claims.get("user_id")
    
    # For now, using headers (implement JWT later):
    tenant_id = request.headers.get("X-Tenant-ID")
    user_id = request.headers.get("X-User-ID")
    
    if tenant_id and user_id:
        db = SessionLocal()
        try:
            from app.db.rls import set_rls_context
            set_rls_context(db, tenant_id, user_id)
            request.state.db = db
            request.state.tenant_id = tenant_id
            request.state.user_id = user_id
        finally:
            db.close()
    
    response = await call_next(request)
    return response
```

### 2. Use RLS-Aware Database Sessions in Endpoints
Option A - Using dependency injection:

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db_with_rls
from app.db.models.document import Document

router = APIRouter()

@router.get("/documents/")
def list_documents(session: Session = Depends(get_db_with_rls)):
    # RLS context is automatically set by the dependency
    documents = session.query(Document).all()
    return documents
```

Option B - Manual context setting:

```python
from app.db.session import SessionLocal
from app.db.rls import set_rls_context

@router.get("/documents/")
def list_documents(request: Request):
    db = SessionLocal()
    try:
        set_rls_context(db, request.state.tenant_id, request.state.user_id)
        documents = db.query(Document).all()
        return documents
    finally:
        db.close()
```

### 3. Important: Always Set RLS Context Before Queries
**Critical:** For RLS to work, context MUST be set before ANY database operation:

```python
# ❌ WRONG - context not set
session = SessionLocal()
documents = session.query(Document).all()  # RLS won't filter

# ✅ CORRECT - context set first
session = SessionLocal()
set_rls_context(session, tenant_id, user_id)
documents = session.query(Document).all()  # RLS filters correctly
```

## Testing RLS

### Test 1: Verify Tenant Isolation
```bash
# Terminal 1: Set Tenant A context
docker exec postgres_db psql -U admin -d app_db << EOF
SELECT set_config('app.tenant_id', '550e8400-e29b-41d4-a716-446655440000', true);
SELECT * FROM documents;
EOF

# Terminal 2: Set Tenant B context
docker exec postgres_db psql -U admin -d app_db << EOF
SELECT set_config('app.tenant_id', '660e8400-e29b-41d4-a716-446655440111', true);
SELECT * FROM documents;
EOF
```

### Test 2: Verify RLS is Enforced
```bash
# Without context - should return no rows (RLS blocks)
docker exec postgres_db psql -U admin -d app_db -c "SELECT * FROM documents;"

# With context - should return filtered rows
docker exec postgres_db psql -U admin -d app_db << EOF
SELECT set_config('app.tenant_id', '550e8400-e29b-41d4-a716-446655440000', true);
SELECT * FROM documents;
EOF
```

## Configuration Checklist

- [ ] Update `app/main.py` middleware to extract tenant_id from JWT
- [ ] Update `app/main.py` middleware to extract user_id from JWT
- [ ] Replace header-based auth with real JWT token validation
- [ ] Update endpoints to use `get_db_with_rls` dependency
- [ ] Test RLS filtering with multiple tenants
- [ ] Test INSERT permission checks
- [ ] Test UPDATE/DELETE owner restrictions
- [ ] Add integration tests for RLS

## Future Enhancements

1. **INSERT/UPDATE/DELETE polices for other tables:** Currently, only SELECT and owner policies are defined. Add INSERT policies for users, proposals, etc.

2. **Role-based access:** Add column-level security or additional policies based on user roles.

3. **Audit logging:** Log RLS policy violations for security.

4. **Performance monitoring:** Monitor RLS overhead on queries.

## Troubleshooting

**"policy ... for table ... already exists" error:**
```bash
docker exec postgres_db psql -U admin -d app_db << EOF
DROP POLICY IF EXISTS tenant_isolation_policy ON documents;
DROP POLICY IF EXISTS insert_tenant_check ON documents;
DROP POLICY IF EXISTS owner_update_policy ON documents;
DROP POLICY IF EXISTS owner_delete_policy ON documents;
EOF
```

**RLS not filtering (context not set):**
- Verify `set_rls_context()` is called before query
- Check `app.tenant_id` and `app.user_id` in PostgreSQL:
```bash
docker exec postgres_db psql -U admin -d app_db -c "SELECT current_setting('app.tenant_id');"
```

**Permission denied on UPDATE/DELETE:**
- Verify `created_by` matches `app.user_id` setting
- Check owner_update_policy and owner_delete_policy exist

## References

- [PostgreSQL RLS Documentation](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [Alembic Migration Versions](alembic/versions/)
- [Database Models](app/db/models/)
