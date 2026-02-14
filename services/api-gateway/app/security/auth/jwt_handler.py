from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple

import os
import uuid
import json

import jwt
from fastapi import HTTPException, status

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ed25519

from app.security.auth.config import settings


# --- Simple helpers used by existing codebase
def create_access_token(user_id: str) -> str:
    payload: Dict[str, Any] = {
        "sub": user_id,
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MIN
        ),
        "iat": datetime.now(timezone.utc),
    }

    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    return token


def create_refresh_token(user_id: str) -> str:
    payload: Dict[str, Any] = {
        "sub": user_id,
        "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        ),
        "iat": datetime.now(timezone.utc),
    }

    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    return token


def verify_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


# --- Advanced multi-alg handler with rotation helpers
KEYS_DIR = os.getenv("JWT_KEYS_DIR", "/app/app/security/auth/keys")
ACTIVE_KID_FILE = os.path.join(KEYS_DIR, "active_kid.json")
DEFAULT_ALGO = os.getenv("JWT_DEFAULT_ALGO", "RS256")


def _read_active_kids() -> Dict[str, str]:
    try:
        with open(ACTIVE_KID_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _write_active_kid(algo: str, kid: str):
    data = _read_active_kids()
    data[algo] = kid
    os.makedirs(KEYS_DIR, exist_ok=True)
    with open(ACTIVE_KID_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)


def _key_paths_for(kid: str) -> Tuple[str, str]:
    priv = os.path.join(KEYS_DIR, f"{kid}_private.pem")
    pub = os.path.join(KEYS_DIR, f"{kid}_public.pem")
    return priv, pub


class JWTHandler:
    """Multi-algorithm JWT helper supporting RS256, HS256 and EdDSA (Ed25519).

    This coexists with the simpler helper functions above for backward compatibility.
    """

    def __init__(self, issuer: Optional[str] = None):
        self.issuer = issuer or os.getenv("JWT_ISSUER", "api-gateway")
        self.secret = settings.SECRET_KEY

    def generate_token(self, subject: str, expires_delta: timedelta, algo: Optional[str] = None, extra_claims: Optional[Dict[str, Any]] = None) -> str:
        now = datetime.utcnow()
        payload: Dict[str, Any] = {
            "iss": self.issuer,
            "sub": subject,
            "iat": int(now.timestamp()),
            "exp": int((now + expires_delta).timestamp()),
            "jti": str(uuid.uuid4()),
        }
        if extra_claims:
            payload.update(extra_claims)

        return self._sign(payload, algo or DEFAULT_ALGO)

    def generate_pair(self, subject: str, access_expires: Optional[timedelta] = None, refresh_expires: Optional[timedelta] = None, algo: Optional[str] = None):
        access_expires = access_expires or timedelta(minutes=15)
        refresh_expires = refresh_expires or timedelta(days=7)
        access = self.generate_token(subject, access_expires, algo, extra_claims={"typ": "access"})
        refresh = self.generate_token(subject, refresh_expires, algo, extra_claims={"typ": "refresh"})
        return access, refresh

    def _sign(self, payload: Dict[str, Any], algo: str) -> str:
        algo = algo.upper()
        if algo == "HS256":
            if not self.secret:
                raise RuntimeError("JWT_SECRET is required for HS256")
            return jwt.encode(payload, self.secret, algorithm="HS256")

        active = _read_active_kids()
        kid = active.get(algo)
        if not kid:
            raise RuntimeError(f"No active kid for algorithm {algo}")

        priv_path, _ = _key_paths_for(kid)
        if not os.path.exists(priv_path):
            raise FileNotFoundError(f"Private key not found: {priv_path}")

        with open(priv_path, "rb") as f:
            key_pem = f.read()

        if algo == "RS256":
            return jwt.encode(payload, key_pem, algorithm="RS256", headers={"kid": kid})
        if algo == "EDDSA":
            return jwt.encode(payload, key_pem, algorithm="EdDSA", headers={"kid": kid})

        raise ValueError(f"Unsupported signing algorithm: {algo}")

    def validate(self, token: str, leeway: int = 10) -> Dict[str, Any]:
        unverified_header = jwt.get_unverified_header(token)
        alg = unverified_header.get("alg")
        kid = unverified_header.get("kid")

        if alg.upper() == "HS256":
            if not self.secret:
                raise RuntimeError("JWT_SECRET is required for HS256 verification")
            return jwt.decode(token, self.secret, algorithms=["HS256"], options={"verify_aud": False}, leeway=leeway)

        if not kid:
            raise RuntimeError("No kid in token header for asymmetric algorithm")

        _, pub_path = _key_paths_for(kid)
        if not os.path.exists(pub_path):
            raise FileNotFoundError(f"Public key not found: {pub_path}")

        with open(pub_path, "rb") as f:
            pub_pem = f.read()

        return jwt.decode(token, pub_pem, algorithms=[alg], options={"verify_aud": False}, leeway=leeway)

    def rotate_rsa_keypair(self, key_size: int = 2048) -> str:
        kid = uuid.uuid4().hex
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)
        priv_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        pub_bytes = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        priv_path, pub_path = _key_paths_for(kid)
        os.makedirs(KEYS_DIR, exist_ok=True)
        with open(priv_path, "wb") as f:
            f.write(priv_bytes)
        with open(pub_path, "wb") as f:
            f.write(pub_bytes)
        _write_active_kid("RS256", kid)
        return kid

    def rotate_ed25519_keypair(self) -> str:
        kid = uuid.uuid4().hex
        private = ed25519.Ed25519PrivateKey.generate()
        priv_bytes = private.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        pub_bytes = private.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        priv_path, pub_path = _key_paths_for(kid)
        os.makedirs(KEYS_DIR, exist_ok=True)
        with open(priv_path, "wb") as f:
            f.write(priv_bytes)
        with open(pub_path, "wb") as f:
            f.write(pub_bytes)
        _write_active_kid("EdDSA", kid)
        return kid


__all__ = ["create_access_token", "create_refresh_token", "verify_token", "JWTHandler"]
