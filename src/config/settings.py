from pydantic_settings import BaseSettings


class BaseAppSettings(BaseSettings):
    # Mongo DB
    mongodb_hosts: str = "host.docker.internal:27017"
    mongodb_db: str = "test"
    mongodb_tls: bool = False
    mongodb_user: str = ""
    mongodb_pw: str = ""
    mongodb_tls_ca_file: str = ""
    account_collection: str = "account-collection"
    seen_collection: str = "seen-collection"
    like_collection: str = "like-collection"
    dislike_collection: str = "dislike-collection"
    match_collection: str = "match-collection"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = BaseAppSettings()
