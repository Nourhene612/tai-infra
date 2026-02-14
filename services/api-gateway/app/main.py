from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging
from uuid import UUID
from app.api.routes import api_router
logger = logging.getLogger(__name__)

app = FastAPI(title="TenderAI API Gateway")


# RLS Context Middleware
@app.middleware("http")
async def rls_context_middleware(request: Request, call_next):
    """
    Middleware to set RLS context for each request.
    Extracts tenant_id and user_id from request context (JWT claims, headers, etc.)
    """
    # TODO: Extract tenant_id and user_id from JWT token or request context
    # Example extract from headers:
    # tenant_id = request.headers.get("X-Tenant-ID")
    # user_id = request.headers.get("X-User-ID")
    
    # For now, pass through - update when auth system is integrated
    response = await call_next(request)
    return response

@app.get("/")
def root():
    return {"status": "ok", "service": "api-gateway"}

@app.get("/health")
def health_check():
    return {"status": "healthy"} 
app.include_router(api_router)