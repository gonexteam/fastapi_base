from fastapi import APIRouter, Depends

from server.api.endpoints.address_end import address_router
from server.api.endpoints.auth_end import auth_router
from server.api.endpoints.comment_end import comment_router
from server.api.endpoints.crop_end import crop_router
from server.api.endpoints.farm_end import farm_router
from server.api.endpoints.pest_end import pest_router
from server.api.endpoints.plant_end import plant_router
from server.api.endpoints.record_end import record_router
from server.api.endpoints.user_end import user_router
from server.api.endpoints.hello_end import hello_router
from server.core.key import validate_request

router = APIRouter()

router.include_router(auth_router,
                      prefix="/auth", tags=["Auth"])
router.include_router(address_router,
                      prefix="/address", tags=["Auth"])
router.include_router(user_router,
                      prefix="/users", tags=["Auth"])
router.include_router(hello_router,
                      prefix="/hello",
                      dependencies=[Depends(validate_request)]
                      )
router.include_router(farm_router, prefix="/farms", tags=["Farm"])
router.include_router(plant_router, prefix="/plants", tags=["Plant"])
router.include_router(crop_router, prefix="/crops", tags=["Crop"])
router.include_router(record_router, prefix="/records", tags=["Record"])
router.include_router(pest_router, prefix="/pests", tags=["Pest"])
router.include_router(comment_router, prefix="/comments", tags=["Comment"])
