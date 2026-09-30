from bot.config import get_settings


def help_text() -> str:
    family = get_settings().family_names
    return f"""
👨‍👩‍👧 <b>Семейный бот</b> — для {family}.

<b>🛒 Покупки</b>
• <code>/buy молоко</code> — добавить в список
• <code>/buys</code> — показать список
• <code>/buyclear</code> — очистить купленное

<b>📝 Заметки</b>
• <code>/note Заголовок | Текст</code> — создать заметку
• <code>/notes</code> — все заметки

<b>📅 Важные даты</b>
• <code>/date 14.02 Годовщина</code> — добавить дату (ДД.ММ или ДД.ММ.ГГГГ)
• <code>/dates</code> — список дат

<b>⏰ Напоминания</b>
• <code>/remind 30м Купить цветы</code> — через 30 минут
• <code>/remind 2ч Созвон</code> — через 2 часа
• <code>/remind 25.12 10:00 Подарки</code> — точное время
• <code>/reminds</code> — активные напоминания

Кнопки меню внизу дублируют команды просмотра.
""".strip()
