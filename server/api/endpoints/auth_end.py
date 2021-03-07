from fastapi import Depends, FastAPI, HTTPException, Form, APIRouter, Query
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import EmailStr
from starlette.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_200_OK

from server.core.email.sendgrid import verification_email
from server.core.key import validate_request
from server.core.security import get_key_hash
from server.db.helpers.user_helper import is_email_available, reset_api, verify_email, update_password
from server.db.crud.user_crud import create_api_user
from server.db.mongodb import get_database
from server.models.user import BaseUserCreate, User

auth_router = APIRouter()

app = FastAPI()


@auth_router.post("/register")
async def register_user(
        user_email: EmailStr = Form(...),
        user_password: str = Form(...),
        db: AsyncIOMotorClient = Depends(get_database)
):
    """
    Endpoint to user register
    """
    if user_password:
        user_password = get_key_hash(user_password)
    user: BaseUserCreate = BaseUserCreate(email=user_email, password=user_password)

    if user:
        await is_email_available(db, user_email)
        api_key = await create_api_user(db, user, False, None)
        await verification_email(api_key, user_email)
        return JSONResponse({user_email: api_key})
    else:
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No Email address provided to create API user",
        )


@auth_router.post("/login")
async def login_user(
        user_email: EmailStr = Form(...),
        user_password: str = Form(...),
        db: AsyncIOMotorClient = Depends(get_database)
):
    """
    Endpoint to user login
    """
    user: BaseUserCreate = BaseUserCreate(email=user_email, password=user_password)
    if user:
        await reset_api(db, user_email, user_password)
    else:
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No Email provided to reset the API Key"
        )


@auth_router.get("/verify")
async def verify(
        email: EmailStr = Query(None),
        db: AsyncIOMotorClient = Depends(get_database)
):
    """After creation of user account, verification email will be sent to the registered
    email id; which will contain a verification link to verify the email. This route is
    to verify the email.
    """
    if email:
        await verify_email(db, email)
        raise HTTPException(
            status_code=HTTP_200_OK,
            detail=f"{email} is now verified! You can start using your API key."
        )
    else:
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No Email to verify"
        )


@auth_router.put("/change_password")
async def change_password(current_user: User = Depends(validate_request),
                          user_password: str = Form(...),
                          db: AsyncIOMotorClient = Depends(get_database)):
    """Edit user password. """
    if user_password:
        user_password = get_key_hash(user_password)
    user = BaseUserCreate(email=current_user.email, password=user_password)
    await update_password(db, user)
