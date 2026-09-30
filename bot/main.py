import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode

from bot.config import get_settings
from bot.db import init_db
from bot.handlers import setup_routers
from bot.middlewares import AccessMiddleware
from bot.services import ReminderScheduler


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )

    settings = get_settings()
    await init_db()

    session = (
        AiohttpSession(proxy=settings.telegram_proxy)
        if settings.telegram_proxy
        else AiohttpSession()
    )
    bot = Bot(
        token=settings.bot_token,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.message.middleware(AccessMiddleware())
    dp.callback_query.middleware(AccessMiddleware())
    dp.include_router(setup_routers())

    scheduler = ReminderScheduler(bot)
    scheduler.start()

    logging.getLogger(__name__).info(
        "Family bot started. Members: %s",
        settings.family_members,
    )

    try:
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
