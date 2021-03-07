"""
Helper functions
"""
import secrets
from typing import Optional

from datetime import datetime
from pydantic import EmailStr
from starlette.exceptions import HTTPException
from starlette.status import (
    HTTP_200_OK,
    HTTP_204_NO_CONTENT,
    HTTP_422_UNPROCESSABLE_ENTITY,
)
from server.core.security import get_key_hash, generate_salt, verify_key
from server.db.mongodb import AsyncIOMotorClient
from server.db.crud.user_crud import get_user_by_email, update_api_user, update_api_user_password
from server.models.user import BaseUserUpdate, BaseUserCreate
from server.core.email.sendgrid import reset_email


async def is_email_available(
        db: AsyncIOMotorClient,
        email: Optional[EmailStr] = None
):
    """Check to see if an email address is available in the database
    :param db: AsyncIOMotorClient connection
    :param email: email address to check
    :return: user details if found or raise HTTPException
    """
    if email:
        user_by_email = await get_user_by_email(db, email)
        if user_by_email:
            raise HTTPException(
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                detail="User with this email already exists",
            )


async def reset_api(
        db: AsyncIOMotorClient,
        email: Optional[EmailStr] = None,
        password: Optional[str] = None
):
    """Reset an API Key
    :param db: AsyncIOMotorClient connection
    :param email: email address to reset api key for
    :param password: password to reset api key for
    :return: raise HTTPExceptions appropriately
    """
    if email and password:
        user: BaseUserUpdate = BaseUserUpdate(email=email)
        user_by_email = await get_user_by_email(db, email)
        if user_by_email:
            if not user_by_email.is_active:
                raise HTTPException(
                    status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Email is not verified!"
                )
            if user_by_email.disabled:
                raise HTTPException(
                    status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="This user is disabled! Cannot reset API Key"
                )
            if not verify_key(password, user_by_email.password):
                raise HTTPException(
                    status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Password is not verified!"
                )
            new_salt = generate_salt()
            new_api_key = secrets.token_urlsafe(32)
            user.salt = new_salt
            user.hashed_api_key = get_key_hash(new_salt + new_api_key)
            await update_api_user(db, email, user)
            await reset_email(new_api_key, email)

            raise HTTPException(
                status_code=HTTP_200_OK,
                detail=f"New API Key for {email} is {new_api_key}"
            )

    else:
        raise HTTPException(
            status_code=HTTP_204_NO_CONTENT,
            detail="No Email provided to reset API Key"
        )


async def verify_email(
        db: AsyncIOMotorClient,
        email: Optional[EmailStr] = None
):
    """Validate an email address after account creation
    :param db: AsyncIOMotorClient connection
    :param email: email address to verify
    :return: raise HTTPExceptions appropriately
    """
    if email:
        user: BaseUserUpdate = BaseUserUpdate(email=email)

        user_by_email = await get_user_by_email(db, email)
        if user_by_email:
            if user_by_email.disabled:
                # user is disabled
                raise HTTPException(
                    status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="User is disabled. Cannot verify user email address"
                )
            if user_by_email.is_active:
                # email is already validated
                raise HTTPException(
                    status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Email is already verified and active"
                )
            else:
                user.updated_at = datetime.utcnow()
                user.is_active = True
                await update_api_user(db, email, user)
        else:
            raise HTTPException(
                status_code=HTTP_204_NO_CONTENT,
                detail="Email not found"
            )
    else:
        raise HTTPException(
            status_code=HTTP_204_NO_CONTENT,
            detail="No Email to validate"
        )


async def deactivate_email(
        db: AsyncIOMotorClient,
        email: Optional[EmailStr] = None
):
    """Disable an enabled user
    :param db: AsyncIOMotorClient connection
    :param email: email address to deactivate
    :return: raise HTTPExceptions appropriately
    """
    user: BaseUserUpdate = BaseUserUpdate(email=email)
    if email:
        user_by_email = await get_user_by_email(db, email)

        if user_by_email:
            if not user_by_email.disabled:
                user.updated_at = datetime.utcnow()
                user.disabled = True
                await update_api_user(db, email, user)
            else:
                raise HTTPException(
                    status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="User already disabled!"
                )
    else:
        raise HTTPException(
            status_code=HTTP_204_NO_CONTENT,
            detail="No Email to validate"
        )


async def activate_email(
        db: AsyncIOMotorClient,
        email: Optional[EmailStr] = None
):
    """Enable a disabled user
    :param db: AsyncIOMotorClient connection
    :param email: email address to activate
    :return: raise HTTPExceptions appropriately
    """
    user: BaseUserUpdate = BaseUserUpdate(email=email)
    if email:
        user_by_email = await get_user_by_email(db, email)

        if user_by_email:
            if user_by_email.disabled:
                user.updated_at = datetime.utcnow()
                user.disabled = False
                await update_api_user(db, email, user)
            else:
                raise HTTPException(
                    status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="User already enabled!"
                )
    else:
        raise HTTPException(
            status_code=HTTP_204_NO_CONTENT,
            detail="No Email to validate"
        )


async def update_password(conn: AsyncIOMotorClient, user: BaseUserCreate):
    user_by_email = await get_user_by_email(conn, user.email)
    if not user_by_email:
        raise HTTPException(
            status_code=HTTP_204_NO_CONTENT,
            detail="No Email to validate"
        )
    if user_by_email.disabled:
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User is locked"
        )
    if not user_by_email.is_active:
        raise HTTPException(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User is not activate"
        )
    await update_api_user_password(conn, user)
    raise HTTPException(
        status_code=HTTP_200_OK,
        detail="Update user success"
    )
