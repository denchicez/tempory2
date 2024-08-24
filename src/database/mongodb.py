from typing import Tuple, List, Optional, Union
from urllib.parse import quote

from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import InvalidURI

from src.config.settings import settings


def get_client():
    url = (
        f"mongodb://{quote(settings.mongodb_user)}:{quote(settings.mongodb_pw)}@{quote(settings.mongodb_hosts)}"
        f"/?authSource={quote(settings.mongodb_db)}"
    )

    if not settings.mongodb_user:
        url = f"mongodb://{quote(settings.mongodb_hosts)}/?authSource={quote(settings.mongodb_db)}"

    try:
        if settings.mongodb_tls:
            client = AsyncIOMotorClient(
                url, tls=settings.mongodb_tls, tlsCAFile=settings.mongodb_tls_ca_file
            )
        else:
            client = AsyncIOMotorClient(url)
    except InvalidURI as e:
        print(f"Проблемы со созданием клиента БД : {e}")
        client = None
    return client


mongo_db_client = get_client()


def get_db():
    try:
        return mongo_db_client[settings.mongodb_db]
    except Exception as e:
        print(f"Проблемы с подключением к БД : {e}")


db = get_db()


async def create_or_check_indexes(
        collection_name: str, indexes: List[List[Tuple[str, int]]]
):
    collection = db[collection_name]

    # Проверяем наличие индекса
    index_info = await collection.index_information()
    for i in indexes:
        if i in [index["key"] for index in index_info.values()]:
            print(
                f"Индекс {i} в коллекции {collection_name} был создан ранее. Добавление не требуется"
            )
        else:
            await collection.create_index(i)
            print(f"Индекс {i} в коллекции {collection_name} успешно создан")


async def get_item(item_id: Union[int, str], collection) -> Optional[dict]:
    try:
        result = await db[collection].find_one({"id": item_id})
        if result is None:
            return None
        return result
    except Exception as e:
        # Обработка других возможных ошибок
        # ...
        raise e  # Повторное возбуждение исключения для передачи его выше


async def get_items(type_class, collection) -> list:
    items = []
    async for item in db[collection].find():
        items.append(type_class(**item))
    return items


async def get_items_by_ids(type_class, ids: list, collection) -> list:
    items_list = await db[collection].find({"id": {"$in": ids}}).to_list(length=None)
    return [type_class(**item) for item in items_list]


async def get_items_query(
        type_class, collection: str, query: dict, sort: list = None
) -> list:
    # projection = {"_id": False}  # Указываем, что поле "_id" должно быть исключено
    # cursor = db[collection].find(query, projection=projection)
    cursor = db[collection].find(query)
    if sort:
        cursor = cursor.sort(sort)
    # documents = await cursor.to_list(length=None)
    # return documents
    items = []
    async for item in cursor:
        items.append(type_class(**item))
    return items


async def inset_item(item: dict, collection) -> str:
    # Проверяем наличие объекта в базе данных
    existing_item = await db[collection].find_one({"id": item["id"]})
    if existing_item:
        # Если объект уже существует, то выбрасываем исключение HTTPException с кодом состояния 409 Conflict
        message = f"Объект уже существует {item}"
        print(message)
        raise HTTPException(status_code=409, detail=message)
    try:
        # Попытка вставить объект
        result = await db[collection].insert_one(item)
        if result.inserted_id:
            message = f"Объект успешно вставлен {result.inserted_id}"
            print(message)
            return str(result.inserted_id)
        else:
            # Ошибка вставки объекта
            message = f"Ошибка вставки объекта {item}"
            print(message)
            raise HTTPException(status_code=500, detail=message)
    except Exception as e:
        message = f"Ошибка вставки объекта {item}: {str(e)}"
        print(message)
        raise HTTPException(status_code=500, detail=message)


async def update_item(item: dict, collection: str) -> dict:
    try:
        result = await db[collection].find_one_and_replace(
            filter={"id": item["id"]}, replacement=item, return_document=True
        )
        if result is None:
            message = (
                f"Ошибка при обновлении документа {item['id']}, документ не найден"
            )
            print(message)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
        return result
    except Exception as e:
        message = f"Ошибка при обновлении документа {item}: {str(e)}"
        print(message)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message
        )


async def update_by_id_item(item_id: str, updated_doc: dict, collection: str) -> dict:
    try:
        result = await db[collection].update_one(
            {"id": item_id}, {"$set": updated_doc}
        )
        if result is None:
            message = (
                f"Ошибка при обновлении по id документа {item_id}, документ не найден"
            )
            print(message)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
        return result
    except Exception as e:
        message = f"Ошибка при обновлении по id документа {item_id}: {str(e)}"
        print(message)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message
        )


async def upsert_item(item, collection: str) -> dict:
    try:
        item_id = item["id"]
        result = await db[collection].replace_one(
            filter={"id": item_id}, replacement=item, upsert=True
        )
        if result.upserted_id is not None:
            message = f"Новый документ был создан id {result.upserted_id}"
            print(message)
            return item
        elif result.modified_count > 0:
            message = f"Существующий документ был обновлен id {item_id}"
            print(message)
            return item
        else:
            message = f"Ошибка при вставке/обновлении документа {item}"
            print(message)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
    except Exception as e:
        message = f"Ошибка при вставке/обновлении документа {item}: {str(e)}"
        print(message)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message
        )


async def delete_item(item_id: str, collection: str) -> None:
    try:
        result = await db[collection].delete_one({"id": item_id})
        if result.deleted_count == 0:
            message = f"Ошибка при удалении документа id {item_id}"
            print(message)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
    except Exception as e:
        message = f"Ошибка при удалении документа id {item_id}: {str(e)}"
        print(message)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message
        )


async def delete_by_query_item(query: dict, collection: str) -> None:
    try:
        result = await db[collection].delete_many(query)
        if result.deleted_count == 0:
            message = f"Ошибка при удалении документа по запросу {query}"
            print(message)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
    except Exception as e:
        message = f"Ошибка при удалении документа по запросу {query}: {str(e)}"
        print(message)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message
        )
