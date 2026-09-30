from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select

from bot.db import Note, SessionLocal
from bot.keyboards import note_keyboard

router = Router(name="notes")


@router.message(Command("note"))
async def cmd_note(message: Message, command: CommandObject) -> None:
    raw = (command.args or "").strip()
    if "|" not in raw:
        await message.answer("Пример: <code>/note Идея ужина | Паста с креветками</code>")
        return

    title, body = [part.strip() for part in raw.split("|", 1)]
    if not title or not body:
        await message.answer("Нужны и заголовок, и текст через |")
        return

    async with SessionLocal() as session:
        note = Note(title=title, body=body, created_by=message.from_user.id)
        session.add(note)
        await session.commit()
        await session.refresh(note)

    await message.answer(
        f"📝 <b>{note.title}</b>\n{note.body}",
        reply_markup=note_keyboard(note.id),
    )


@router.message(Command("notes"))
@router.message(F.text == "📝 Заметки")
async def cmd_notes(message: Message) -> None:
    async with SessionLocal() as session:
        result = await session.execute(select(Note).order_by(Note.id.desc()))
        notes = result.scalars().all()

    if not notes:
        await message.answer("Заметок пока нет. Создай: /note Заголовок | Текст")
        return

    await message.answer(f"📝 Заметок: {len(notes)}")
    for note in notes:
        await message.answer(
            f"<b>{note.title}</b>\n{note.body}",
            reply_markup=note_keyboard(note.id),
        )


@router.callback_query(F.data.startswith("note:delete:"))
async def delete_note(callback: CallbackQuery) -> None:
    if not callback.data or not callback.message:
        return

    note_id = int(callback.data.split(":")[-1])
    async with SessionLocal() as session:
        note = await session.get(Note, note_id)
        if note is None:
            await callback.answer("Уже удалено", show_alert=True)
            await callback.message.delete()
            return
        title = note.title
        await session.delete(note)
        await session.commit()

    await callback.message.edit_text(f"🗑 Заметка удалена: {title}")
    await callback.answer()
