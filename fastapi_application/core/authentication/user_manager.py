import uuid
from typing import Optional, TYPE_CHECKING

import structlog
from fastapi_users import (
    BaseUserManager,
    UUIDIDMixin,
)
from fastapi_users.db import BaseUserDatabase

from fastapi_application.core.config import settings
from fastapi_application.core.models import User

if TYPE_CHECKING:
    from fastapi import Request, BackgroundTasks
    from fastapi_users.password import PasswordHelperProtocol

logger = structlog.get_logger()


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.access_token.reset_password_token_secret
    verification_token_secret = settings.access_token.verification_token_secret

    def __init__(
        self,
        user_db: BaseUserDatabase[User, uuid.UUID],
        password_helper: Optional["PasswordHelperProtocol"] = None,
        background_tasks: Optional["BackgroundTasks"] = None,
    ):
        super().__init__(user_db, password_helper)
        self.background_tasks = background_tasks

    async def on_after_register(
        self,
        user: User,
        request: Optional["Request"] = None,
    ):
        logger.warning(
            "User %r has registered.",
            user.id,
        )
        # await send_new_user_notification(user)

    async def on_after_forgot_password(
        self,
        user: User,
        token: str,
        request: Optional["Request"] = None,
    ):
        logger.warning(
            "User %r has forgot their password. Reset token: %r",
            user.id,
            token,
        )

    async def on_after_request_verify(
        self,
        user: User,
        token: str,
        request: Optional["Request"] = None,
    ):
        logger.warning(
            "Verification requested for user %r. Verification token: %r",
            user.id,
            token,
        )
        # verification_link = request.url_for("verify_email").replace_query_params(
        #     token=token
        # )
        # self.background_tasks.add_task(
        #     send_verification_email,
        #     user=user,
        #     verification_link=str(verification_link),
        # )

    async def on_after_verify(
        self,
        user: User,
        request: Optional["Request"] = None,
    ):
        logger.warning(
            "User %r has been verified",
            user.id,
        )

        # self.background_tasks.add_task(
        #     send_email_confirmed,
        #     user=user,
        # )
