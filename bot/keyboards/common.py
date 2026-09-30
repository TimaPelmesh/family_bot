from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 Покупки"), KeyboardButton(text="📝 Заметки")],
            [KeyboardButton(text="📅 Даты"), KeyboardButton(text="⏰ Напоминания")],
            [KeyboardButton(text="ℹ️ Помощь")],
        ],
        resize_keyboard=True,
    )


def shopping_item_keyboard(item_id: int, is_bought: bool) -> InlineKeyboardMarkup:
    action = "bought" if not is_bought else "unbought"
    label = "✅ Куплено" if not is_bought else "↩️ Вернуть"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=label,
                    callback_data=f"shop:{action}:{item_id}",
                ),
                InlineKeyboardButton(
                    text="🗑",
                    callback_data=f"shop:delete:{item_id}",
                ),
            ]
        ]
    )


def note_keyboard(note_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🗑 Удалить",
                    callback_data=f"note:delete:{note_id}",
                )
            ]
        ]
    )


def date_keyboard(date_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🗑 Удалить",
                    callback_data=f"date:delete:{date_id}",
                )
            ]
        ]
    )


def reminder_keyboard(reminder_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🗑 Удалить",
                    callback_data=f"remind:delete:{reminder_id}",
                )
            ]
        ]
    )
