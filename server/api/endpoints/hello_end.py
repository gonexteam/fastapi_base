
from fastapi import APIRouter

hello_router = APIRouter()


@hello_router.get("/")
async def home():
    return "Hello World"
