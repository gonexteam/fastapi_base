from fastapi import APIRouter, Depends

from server.api.endpoints.auth_end import auth_router
from server.api.endpoints.user_end import user_router
from server.api.endpoints.hello_end import hello_router
from server.core.key import validate_request

router = APIRouter()

router.include_router(auth_router,
                      prefix="/auth", tags=["Auth"])
router.include_router(user_router,
                      prefix="/users", tags=["Auth"])
router.include_router(hello_router,
                      prefix="/hello",
                      dependencies=[Depends(validate_request)]
                      )
