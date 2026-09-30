import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from bot.config import get_settings
from bot.db import Reminder, SessionLocal

logger = logging.getLogger(__name__)


class ReminderScheduler:
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.settings = get_settings()
        self.scheduler = AsyncIOScheduler(timezone=ZoneInfo(self.settings.timezone))

    def start(self) -> None:
        self.scheduler.add_job(
            self._tick,
            trigger="interval",
            seconds=30,
            id="reminders_tick",
            replace_existing=True,
            max_instances=1,
        )
        self.scheduler.start()
        logger.info("Reminder scheduler started")

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

    async def _tick(self) -> None:
        now = datetime.now(ZoneInfo(self.settings.timezone))
        async with SessionLocal() as session:
            result = await session.execute(
                select(Reminder).where(
                    Reminder.is_sent.is_(False),
                    Reminder.remind_at <= now,
                )
            )
            due = result.scalars().all()
            for reminder in due:
                author = self.settings.display_name(reminder.created_by)
                for user_id in self.settings.allowed_user_ids:
                    try:
                        await self.bot.send_message(
                            user_id,
                            f"⏰ Напоминание от {author}:\n{reminder.text}",
                        )
                    except Exception:
                        logger.exception(
                            "Failed to send reminder %s to %s",
                            reminder.id,
                            user_id,
                        )
                reminder.is_sent = True
            if due:
                await session.commit()
