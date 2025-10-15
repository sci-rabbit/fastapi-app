from fastapi import APIRouter

from fastapi_application.api.dependencies.authentication.backend import (
    authentication_backend,
)
from fastapi_application.core.authentication.fa_users import fastapi_users
from fastapi_application.core.schemas.auth_schema import UserCreate
from fastapi_application.core.config import settings
from fastapi_application.core.schemas import UserSchema

auth_router = APIRouter(
    prefix=settings.api.v1.auth,
    tags=["Auth"],
)

# /login
# /logout
auth_router.include_router(
    router=fastapi_users.get_auth_router(
        authentication_backend,
        # requires_verification=True,
    ),
)


# /register
auth_router.include_router(
    router=fastapi_users.get_register_router(
        UserSchema,
        UserCreate,
    ),
)

# /request-verify-token
# /verify
auth_router.include_router(
    router=fastapi_users.get_verify_router(UserSchema),
)

# /forgot-password
# /reset-password
auth_router.include_router(
    router=fastapi_users.get_reset_password_router(),
)
