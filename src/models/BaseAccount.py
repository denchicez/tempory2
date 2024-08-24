from pydantic import BaseModel


class BaseAccount(BaseModel):
    id: int
    telegram_id: int
    photo_url: str
    name: str
    birthday: str
    about: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "1488∆",
                    "telegram_id": "1488",
                    "photo_url": "http://127.0.0.1:8001/picture/1488",
                    "name": "Денис",
                    "birthday": "12.12.2002",
                    "about": "Я пишу парсеры"
                }
            ]
        }
    }
