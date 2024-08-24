from fastapi import APIRouter, UploadFile, Response

from src.config import settings
from src.database.mongodb import upsert_item, get_item
from src.models import BaseAccount

register_route = APIRouter(tags=['register'])


@register_route.post("/picture")
async def save_pic(telegram_id: int, file: UploadFile) -> str:
    with open(f"./photos/{telegram_id}.jpg", "wb") as f:
        f.write(await file.read())
    url = f"http://127.0.0.1:8001/picture/{telegram_id}"
    return url


@register_route.get("/picture/{telegram_id}")
async def get_pic(telegram_id: int) -> Response:
    with open(f"./photos/{telegram_id}.jpg", "rb") as f:
        image_bytes = f.read()
    return Response(content=image_bytes, media_type="image/png")


@register_route.post("/account/register")
async def register_account(account: BaseAccount):
    await upsert_item(
        item=account.model_dump(),
        collection=settings.account_collection
    )


@register_route.get("/account/{telegram_id}")
async def get_account(telegram_id: int) -> BaseAccount:
    item = await get_item(
        item_id=telegram_id,
        collection=settings.account_collection
    )
    print(item)
    account = BaseAccount(**item)
    return account


    # @register_route.get("/account/{telegram_id}/likes/")
    # async def get_account_likes(telegram_id: int):
    #     item = await get_item(
    #         item_id=telegram_id,
    #         collection=settings.like_collection
    #     )
    #     account = BaseAccount.model_validate_json(**item)
    #     return account
