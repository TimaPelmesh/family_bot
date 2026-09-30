from __future__ import annotations

import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select

from bot.config import get_settings
from bot.db import Reminder, SessionLocal
from bot.keyboards import reminder_keyboard

router = Router(name="reminders")

RELATIVE_RE = re.compile(
    r"^(?P<amount>\d+)\s*(?P<unit>м|мин|h|ч|д|дн|m|min|d)\s+(?P<text>.+)$",
    re.IGNORECASE,
)
ABSOLUTE_RE = re.compile(
    r"^(?P<day>\d{1,2})\.(?P<month>\d{1,2})(?:\.(?P<year>\d{4}))?\s+"
    r"(?P<hour>\d{1,2}):(?P<minute>\d{2})\s+(?P<text>.+)$"
)


def _tz() -> ZoneInfo:
    return ZoneInfo(get_settings().timezone)


def parse_remind_at(raw: str) -> tuple[datetime, str] | None:
    now = datetime.now(_tz())
    relative = RELATIVE_RE.match(raw)
    if relative:
        amount = int(relative.group("amount"))
        unit = relative.group("unit").lower()
        text = relative.group("text").strip()
        if unit in {"м", "мин", "m", "min"}:
            delta = timedelta(minutes=amount)
        elif unit in {"ч", "h"}:
            delta = timedelta(hours=amount)
        else:
            delta = timedelta(days=amount)
        return now + delta, text

    absolute = ABSOLUTE_RE.match(raw)
    if absolute:
        year = int(absolute.group("year") or now.year)
        remind_at = datetime(
            year,
            int(absolute.group("month")),
            int(absolute.group("day")),
            int(absolute.group("hour")),
            int(absolute.group("minute")),
            tzinfo=_tz(),
        )
        if remind_at <= now and absolute.group("year") is None:
            remind_at = remind_at.replace(year=now.year + 1)
        return remind_at, absolute.group("text").strip()

    return None


@router.message(Command("remind"))
async def cmd_remind(message: Message, command: CommandObject) -> None:
    raw = (command.args or "").strip()
    if not raw:
        await message.answer(
            "Примеры:\n"
            "<code>/remind 30м Купить цветы</code>\n"
            "<code>/remind 2ч Созвон</code>\n"
            "<code>/remind 25.12 10:00 Подарки</code>"
        )
        return

    parsed = parse_remind_at(raw)
    if parsed is None:
        await message.answer("Не понял время. Смотри /help")
        return

    remind_at, text = parsed
    if remind_at <= datetime.now(_tz()):
        await message.answer("Время уже прошло — поставь будущее")
        return

    async with SessionLocal() as session:
        reminder = Reminder(
            text=text,
            remind_at=remind_at,
            created_by=message.from_user.id,
        )
        session.add(reminder)
        await session.commit()
        await session.refresh(reminder)

    await message.answer(
        f"⏰ Напомню {remind_at.strftime('%d.%m.%Y %H:%M')}:\n{text}",
        reply_markup=reminder_keyboard(reminder.id),
    )


@router.message(Command("reminds"))
@router.message(F.text == "⏰ Напоминания")
async def cmd_reminds(message: Message) -> None:
    async with SessionLocal() as session:
        result = await session.execute(
            select(Reminder)
            .where(Reminder.is_sent.is_(False))
            .order_by(Reminder.remind_at)
        )
        items = result.scalars().all()

    if not items:
        await message.answer("Активных напоминаний нет.")
        return

    await message.answer(f"⏰ Активных: {len(items)}")
    for item in items:
        local_at = item.remind_at.astimezone(_tz())
        await message.answer(
            f"<b>{local_at.strftime('%d.%m.%Y %H:%M')}</b>\n{item.text}",
            reply_markup=reminder_keyboard(item.id),
        )


@router.callback_query(F.data.startswith("remind:delete:"))
async def delete_reminder(callback: CallbackQuery) -> None:
    if not callback.data or not callback.message:
        return

    reminder_id = int(callback.data.split(":")[-1])
    async with SessionLocal() as session:
        item = await session.get(Reminder, reminder_id)
        if item is None:
            await callback.answer("Уже удалено", show_alert=True)
            await callback.message.delete()
            return
        text = item.text
        await session.delete(item)
        await session.commit()

    await callback.message.edit_text(f"🗑 Напоминание удалено: {text}")
    await callback.answer()
