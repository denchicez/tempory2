from typing import List

from fastapi import APIRouter, UploadFile, Response

from src.config import settings
from src.database.mongodb import inset_item, get_item, get_items_query
from src.models import BaseAccount, Like, Match, Seen

like_route = APIRouter(tags=['like'])


@like_route.post("/like")
async def set_like(like: Like) -> None:
    # TODO: PUSH
    item = await get_item(
        item_id=f"{like.to_telegram_id}-{like.from_telegram_id}",
        collection=settings.like_collection
    )
    if item is None:
        await inset_item(
            item=like.model_dump(),
            collection=settings.like_collection
        )
    else:
        match = Match(telegram_id1=like.from_telegram_id, telegram_id2=like.to_telegram_id)
        await inset_item(
            item=match.model_dump(),
            collection=settings.match_collection
        )


@like_route.delete("/like")
async def delete_like(like: Like) -> None:
    await get_item(
        item_id=f"{like.to_telegram_id}-{like.from_telegram_id}",
        collection=settings.like_collection
    )
    await inset_item(
        item=like.model_dump(),
        collection=settings.dislike_collection
    )


@like_route.get("/likes")
async def get_likes(telegram_id: int) -> List[BaseAccount]:
    items = await get_items_query(
        type_class=Like,
        collection=settings.like_collection,
        query={
            "to_telegram_id": telegram_id
        }
    )
    accounts = []
    for item in items:
        account = await get_item(item_id=item.from_telegram_id, collection=settings.account_collection)
        accounts.append(BaseAccount(**account))
    return accounts


@like_route.get("/matches")
async def get_matches(telegram_id: int) -> List[Match]:
    items = await get_items_query(
        type_class=Match,
        collection=settings.match_collection,
        query={
            "$or": {
                "telegram_id1": telegram_id,
                "telegram_id2": telegram_id,
            }
        }
    )
    return items


@like_route.get("/cards")
async def get_cards(telegram_id: int) -> List[BaseAccount]:
    items = await get_items_query(
        type_class=BaseAccount,
        collection=settings.account_collection,
        query={
            # "$not": {
            #     "telegram_id": telegram_id
            # }
        }
    )
    items_seen = []
    items_seen += await get_items_query(
        type_class=Like,
        collection=settings.like_collection,
        query={
            "$or": [
                {"from_telegram_id": telegram_id},
                {"to_telegram_id": telegram_id},
            ]
        }
    )
    items_seen += await get_items_query(
        type_class=Like,
        collection=settings.dislike_collection,
        query={
            "$or": [
                {"from_telegram_id": telegram_id},
                {"to_telegram_id": telegram_id},
            ]
        }
    )
    print(items_seen)
    items_seen_id = [item.from_telegram_id if item.from_telegram_id != telegram_id else item.to_telegram_id for item in
                     items_seen]
    new_items = []
    for item in items:
        if item.telegram_id in items_seen_id:
            continue
        new_items.append(item)
    print(new_items)
    return new_items

