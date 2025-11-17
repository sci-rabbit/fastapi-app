import logging
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

BASE_DIR = Path(__file__).resolve().parent.parent


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class LoggingConfig(BaseModel):
    level: str = "INFO"

class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    auth: str = "/auth"
    users: str = "/users"
    products: str = "/products"
    categories: str = "/categories"
    posts: str = "/posts"
    orders: str = "/orders"


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()

    @property
    def bearer_token_url(self) -> str:
        # api/v1/auth/login
        parts = (self.prefix, self.v1.prefix, self.v1.auth, "/login")
        path = "".join(parts)
        # return path[1:]
        return path.removeprefix("/")


class DatabaseConfig(BaseModel):
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10
    user: str
    password: str
    host: str = "localhost"
    port: int = 5432
    name: str

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class RedisConfig(BaseModel):
    host: str
    password: str
    port: str


class AccessToken(BaseModel):
    lifetime_seconds: int = 3600
    reset_password_token_secret: str
    verification_token_secret: str


class RateLimiter(BaseModel):
    times: int = 10
    seconds: int = 60


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )

    run: RunConfig = RunConfig()
    logging: LoggingConfig = LoggingConfig()
    api: ApiPrefix = ApiPrefix()
    redis: RedisConfig
    db: DatabaseConfig
    access_token: AccessToken
    rate_limiter: RateLimiter = RateLimiter()

settings = Settings()
