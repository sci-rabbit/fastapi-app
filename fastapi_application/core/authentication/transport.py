from fastapi_users.authentication import BearerTransport

from fastapi_application.core.config import settings

bearer_transport = BearerTransport(
    tokenUrl=settings.api.bearer_token_url,
)
