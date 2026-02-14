"""Simplified login route for debugging"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.security.auth.password import verify_password
from app.security.auth.jwt_handler import create_access_token, create_refresh_token


router = APIRouter(tags=["Auth"])


@router.post("/login-simple", response_model=TokenResponse)
def login_simple(data: LoginRequest, db: Session = Depends(get_db)):
    """Simplified login that uses raw SQL to test DB connection"""
    try:
        # Test 1: Raw SQL query
        result = db.execute(
            text("SELECT id, hashed_password FROM users WHERE email = :email"),
            {"email": data.email}
        ).first()
        
        if not result:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user_id, hashed_password = result
        
        # Test 2: Verify password
        if not verify_password(data.password, hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Test 3: Generate tokens
        access_token = create_access_token(str(user_id))
        refresh_token = create_refresh_token(str(user_id))
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
