from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from fastapi_application.api.api_v1.views.auth_views import auth_router
from fastapi_application.api.api_v1.views.category_views import category_router
from fastapi_application.api.api_v1.views.order_views import order_router
from fastapi_application.api.api_v1.views.post_views import post_router
from fastapi_application.api.api_v1.views.product_views import product_router
from fastapi_application.api.api_v1.views.user_views import user_router
from fastapi_application.core.authentication.fa_users import current_active_superuser
from fastapi_application.core.config import settings


http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(
    prefix=settings.api.v1.prefix,
    dependencies=[Depends(http_bearer)],
)


router.include_router(user_router, dependencies=[Depends(current_active_superuser)])
router.include_router(post_router)
router.include_router(order_router)
router.include_router(product_router)
router.include_router(category_router)
router.include_router(auth_router)
