from pydantic import BaseModel, model_validator


class Seen(BaseModel):
    id: str = ""
    telegram_id1: int
    telegram_id2: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "1487-1488",
                    "telegram_id1": 1487,
                    "telegram_id2": 1488
                }
            ]
        }
    }

    @model_validator(mode='after')
    def create_id(cls, values):
        if values.telegram_id1 > values.telegram_id2:
            values.telegram_id1, values.telegram_id2 = values.telegram_id2, values.telegram_id1
        values.id = f"{values.telegram_id1}-{values.telegram_id2}"
        return values
