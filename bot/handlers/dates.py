from datetime import date, datetime

from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select

from bot.db import ImportantDate, SessionLocal
from bot.keyboards import date_keyboard

router = Router(name="dates")


def _parse_event_date(raw: str) -> date | None:
    for fmt in ("%d.%m.%Y", "%d.%m"):
        try:
            parsed = datetime.strptime(raw, fmt)
            year = parsed.year if fmt == "%d.%m.%Y" else date.today().year
            return date(year, parsed.month, parsed.day)
        except ValueError:
            continue
    return None


@router.message(Command("date"))
async def cmd_date(message: Message, command: CommandObject) -> None:
    raw = (command.args or "").strip()
    if not raw:
        await message.answer("Пример: <code>/date 14.02 Годовщина</code>")
        return

    parts = raw.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Нужны дата и название. Пример: /date 08.03 Цветы")
        return

    event_date = _parse_event_date(parts[0])
    title = parts[1].strip()
    if event_date is None or not title:
        await message.answer("Дата в формате ДД.ММ или ДД.ММ.ГГГГ")
        return

    async with SessionLocal() as session:
        item = ImportantDate(
            title=title,
            event_date=event_date,
            created_by=message.from_user.id,
        )
        session.add(item)
        await session.commit()
        await session.refresh(item)

    await message.answer(
        f"📅 <b>{item.title}</b> — {item.event_date.strftime('%d.%m.%Y')}",
        reply_markup=date_keyboard(item.id),
    )


@router.message(Command("dates"))
@router.message(F.text == "📅 Даты")
async def cmd_dates(message: Message) -> None:
    async with SessionLocal() as session:
        result = await session.execute(
            select(ImportantDate).order_by(ImportantDate.event_date)
        )
        items = result.scalars().all()

    if not items:
        await message.answer("Важных дат пока нет. Добавь: /date 14.02 Годовщина")
        return

    today = date.today()
    await message.answer(f"📅 Важных дат: {len(items)}")
    for item in items:
        days = (item.event_date.replace(year=today.year) - today).days
        if days < 0:
            days = (item.event_date.replace(year=today.year + 1) - today).days
        suffix = f" (через {days} дн.)" if days else " (сегодня!)"
        await message.answer(
            f"<b>{item.title}</b> — {item.event_date.strftime('%d.%m')}{suffix}",
            reply_markup=date_keyboard(item.id),
        )


@router.callback_query(F.data.startswith("date:delete:"))
async def delete_date(callback: CallbackQuery) -> None:
    if not callback.data or not callback.message:
        return

    date_id = int(callback.data.split(":")[-1])
    async with SessionLocal() as session:
        item = await session.get(ImportantDate, date_id)
        if item is None:
            await callback.answer("Уже удалено", show_alert=True)
            await callback.message.delete()
            return
        title = item.title
        await session.delete(item)
        await session.commit()

    await callback.message.edit_text(f"🗑 Дата удалена: {title}")
    await callback.answer()
