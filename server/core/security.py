"""
Security
"""
from passlib.context import CryptContext

import bcrypt


apikey_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_salt():
    return bcrypt.gensalt().decode()


def verify_key(plain_apikey, hashed_apikey):
    return apikey_context.verify(plain_apikey, hashed_apikey)


def get_key_hash(apikey):
    return apikey_context.hash(apikey)


# def verify_password(plain_password, hashed_password):
#     return apikey_context.verify(plain_password, hashed_password)
#
#
# def get_password_hash(password):
#     return apikey_context.hash(password)


