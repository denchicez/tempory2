from pydantic import BaseModel, model_validator


class Like(BaseModel):
    id: str = ""
    from_telegram_id: int
    to_telegram_id: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "1487-1488",
                    "from_telegram_id": 1487,
                    "to_telegram_id": 1488
                }
            ]
        }
    }

    @model_validator(mode='after')
    def create_id(cls, values):
        values.id = f"{values.from_telegram_id}-{values.to_telegram_id}"
        return values
