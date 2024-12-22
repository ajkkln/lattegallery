from pydantic_settings import BaseSettings, SettingsConfigDict

from lattegallery.accounts.schemas import AccountCreateSchema


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(secrets_dir="/run/secrets")

    db_url: str
    initial_accounts: list[AccountCreateSchema]