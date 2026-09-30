from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from bot.config import get_settings


class AccessMiddleware(BaseMiddleware):
    """Allow only people listed in FAMILY_MEMBERS."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        settings = get_settings()
        allowed = set(settings.allowed_user_ids)

        if user is None or user.id not in allowed:
            if isinstance(event, Message):
                await event.answer(
                    "Этот бот только для нашей семьи 🙂\n"
                    f"Сейчас доступ есть у: {settings.family_names}.\n"
                    "Если ты один из нас — добавь Имя:telegram_id в FAMILY_MEMBERS."
                )
            return None

        return await handler(event, data)
