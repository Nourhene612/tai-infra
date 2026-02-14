"""Debug routes to diagnose issues"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.db.models.user import User
from app.security.auth.config import settings

router = APIRouter(tags=["Debug"])


@router.get("/debug/config")
def debug_config():
    """Check if configuration is loaded correctly"""
    return {
        "SECRET_KEY_SET": bool(settings.SECRET_KEY),
        "JWT_ALGORITHM": settings.JWT_ALGORITHM,
        "ACCESS_TOKEN_EXPIRE_MIN": settings.ACCESS_TOKEN_EXPIRE_MIN,
    }


@router.get("/debug/db")
def debug_db(db: Session = Depends(get_db)):
    """Check if database connection works"""
    try:
        user_count = db.query(User).count()
        return {"status": "ok", "user_count": user_count}
    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.get("/debug/models")
def debug_models():
    """Check if models are loaded"""
    from app.db.base import Base
    tables = sorted(list(Base.metadata.tables.keys()))
    return {"tables": tables}
