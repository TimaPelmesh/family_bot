from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select

from bot.config import get_settings
from bot.db import SessionLocal, ShoppingItem
from bot.keyboards import shopping_item_keyboard

router = Router(name="shopping")


async def _send_list(message: Message) -> None:
    async with SessionLocal() as session:
        result = await session.execute(
            select(ShoppingItem).order_by(ShoppingItem.is_bought, ShoppingItem.id)
        )
        items = result.scalars().all()

    if not items:
        await message.answer("Список покупок пуст. Добавь: /buy молоко")
        return

    settings = get_settings()
    await message.answer("🛒 <b>Список покупок</b>:")
    for item in items:
        mark = "☑️" if item.is_bought else "⬜"
        who = settings.display_name(item.created_by)
        await message.answer(
            f"{mark} {item.title}\n<i>добавил(а): {who}</i>",
            reply_markup=shopping_item_keyboard(item.id, item.is_bought),
        )


@router.message(Command("buy"))
async def cmd_buy(message: Message, command: CommandObject) -> None:
    title = (command.args or "").strip()
    if not title:
        await message.answer("Пример: <code>/buy хлеб</code>")
        return

    async with SessionLocal() as session:
        item = ShoppingItem(title=title, created_by=message.from_user.id)
        session.add(item)
        await session.commit()
        await session.refresh(item)

    await message.answer(
        f"Добавлено в покупки: <b>{item.title}</b>",
        reply_markup=shopping_item_keyboard(item.id, item.is_bought),
    )


@router.message(Command("buys"))
@router.message(F.text == "🛒 Покупки")
async def cmd_buys(message: Message) -> None:
    await _send_list(message)


@router.message(Command("buyclear"))
async def cmd_buyclear(message: Message) -> None:
    async with SessionLocal() as session:
        result = await session.execute(
            select(ShoppingItem).where(ShoppingItem.is_bought.is_(True))
        )
        items = result.scalars().all()
        for item in items:
            await session.delete(item)
        await session.commit()
        count = len(items)

    await message.answer(f"Удалено купленное: {count}")


@router.callback_query(F.data.startswith("shop:"))
async def shopping_callback(callback: CallbackQuery) -> None:
    if not callback.data or not callback.message:
        return

    _, action, raw_id = callback.data.split(":", 2)
    item_id = int(raw_id)

    async with SessionLocal() as session:
        item = await session.get(ShoppingItem, item_id)
        if item is None:
            await callback.answer("Уже нет в списке", show_alert=True)
            await callback.message.delete()
            return

        if action == "delete":
            title = item.title
            await session.delete(item)
            await session.commit()
            await callback.message.edit_text(f"🗑 Удалено: {title}")
            await callback.answer()
            return

        item.is_bought = action == "bought"
        await session.commit()
        mark = "☑️" if item.is_bought else "⬜"
        await callback.message.edit_text(
            f"{mark} {item.title}",
            reply_markup=shopping_item_keyboard(item.id, item.is_bought),
        )
        await callback.answer()
