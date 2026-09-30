from functools import lru_cache
from urllib.parse import quote_plus

from pydantic import Field, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_family_members(raw: str) -> dict[int, str]:
    """Parse 'Тим:111,Аня:222' or 'Тим=111,Аня=222' into {id: name}."""
    members: dict[int, str] = {}
    for chunk in raw.split(","):
        part = chunk.strip()
        if not part:
            continue
        if ":" in part:
            name, user_id = part.rsplit(":", 1)
        elif "=" in part:
            name, user_id = part.rsplit("=", 1)
        else:
            raise ValueError(
                "FAMILY_MEMBERS: each person must be Name:telegram_id, "
                f"got '{part}'"
            )
        name = name.strip()
        user_id = user_id.strip()
        if not name or not user_id.isdigit():
            raise ValueError(
                "FAMILY_MEMBERS: use Имя:цифровой_telegram_id, "
                f"got '{part}'"
            )
        members[int(user_id)] = name
    if not members:
        raise ValueError("FAMILY_MEMBERS cannot be empty")
    return members


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot_token: str = Field(alias="BOT_TOKEN")
    family_members_raw: str = Field(alias="FAMILY_MEMBERS")

    postgres_user: str = Field(alias="POSTGRES_USER")
    postgres_password: str = Field(alias="POSTGRES_PASSWORD")
    postgres_db: str = Field(alias="POSTGRES_DB")
    postgres_host: str = Field(default="db", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")

    timezone: str = Field(default="Europe/Moscow", alias="TIMEZONE")
    telegram_proxy: str | None = Field(default=None, alias="TELEGRAM_PROXY")

    @field_validator("family_members_raw")
    @classmethod
    def family_members_must_parse(cls, value: str) -> str:
        parse_family_members(value)
        return value

    @computed_field  # type: ignore[prop-decorator]
    @property
    def family_members(self) -> dict[int, str]:
        return parse_family_members(self.family_members_raw)

    @property
    def allowed_user_ids(self) -> list[int]:
        return list(self.family_members.keys())

    @property
    def family_names(self) -> str:
        return " и ".join(self.family_members.values())

    def display_name(self, user_id: int | None) -> str:
        if user_id is None:
            return "кто-то"
        return self.family_members.get(user_id, str(user_id))

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{quote_plus(self.postgres_password)}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
