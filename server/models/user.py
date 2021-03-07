"""
DB Model
"""
from pydantic import EmailStr
from typing import Optional

from server.core.security import verify_key, get_key_hash, generate_salt
from server.models.base import DateTimeModelMixin, RWModel


class BaseUser(DateTimeModelMixin, RWModel):
    email: EmailStr
    endpoint_access: list = ["user"]
    is_superuser: bool = False
    is_active: bool = False
    disabled: bool = False


class BaseUserInDB(BaseUser):
    id: str
    hashed_api_key: str = ""
    salt: str = ""
    password: str = ""

    def check_api_key(self, api_key: str):
        return verify_key(self.salt + api_key, self.hashed_api_key)

    def reset_api_key(self, api_key: str):
        self.salt = generate_salt()
        self.hashed_api_key = get_key_hash(self.salt + api_key)


class User(BaseUser):
    id: str
    is_superuser: bool
    is_pro: bool = False
    endpoint_access = list


class BaseUserCreate(RWModel):
    email: EmailStr
    password: str
    phone: Optional[str]


class BaseUserLogin(RWModel):
    hashed_api_key: str
    email: EmailStr


class BaseUserUpdate(BaseUser):
    hashed_api_key: Optional[str] = None
    salt: Optional[str] = None
    disabled: Optional[bool] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    endpoint_access: Optional[list] = None
