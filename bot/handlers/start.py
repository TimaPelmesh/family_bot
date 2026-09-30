from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from bot.config import get_settings
from bot.keyboards import main_menu
from bot.texts import help_text

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    settings = get_settings()
    name = settings.display_name(message.from_user.id if message.from_user else None)
    await message.answer(
        f"Привет, {name}! Это бот для {settings.family_names} 💛\n"
        "Покупки, заметки, даты и напоминания — всё в одном месте.\n\n"
        "Нажми «ℹ️ Помощь» или /help, чтобы увидеть команды.",
        reply_markup=main_menu(),
    )


@router.message(Command("help"))
@router.message(F.text == "ℹ️ Помощь")
async def cmd_help(message: Message) -> None:
    await message.answer(help_text(), reply_markup=main_menu())
