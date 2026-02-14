from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Secrets (override in env or secret manager in production)
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"

    # Expiration settings
    ACCESS_TOKEN_EXPIRE_MIN: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Optional keys directory for asymmetric algorithms
    JWT_KEYS_DIR: str = "/app/app/security/auth/keys"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
