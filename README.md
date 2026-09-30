<<<<<<< HEAD
# Семейный Telegram-бот для двоих

Общий бот для покупок, заметок, важных дат и напоминаний. Работает в Docker с PostgreSQL. Доступ только у людей из `FAMILY_MEMBERS`.

## Что умеет (MVP)

| Раздел | Команды |
|--------|---------|
| Покупки | `/buy`, `/buys`, `/buyclear` + кнопки «куплено / удалить» |
| Заметки | `/note Заголовок \| Текст`, `/notes` |
| Даты | `/date 14.02 Годовщина`, `/dates` |
| Напоминания | `/remind 30м …`, `/remind 25.12 10:00 …`, `/reminds` |

Напоминание уходит **обоим** из whitelist.

## Быстрый старт

### 1. Токен бота

1. Напиши [@BotFather](https://t.me/BotFather) → `/newbot`
2. Сохрани токен
3. Узнай свои ID у [@userinfobot](https://t.me/userinfobot) (ты и девушка) — без ID Telegram не отличит человека, имя в env только для вас

### 2. Настрой env

```bash
cp .env.example .env
```

Отредактируй `.env`:

- `BOT_TOKEN` — токен от BotFather
- `FAMILY_MEMBERS` — кто имеет доступ, в формате `Тим:111111111,Аня:222222222`
- `POSTGRES_PASSWORD` — свой пароль
- `TIMEZONE` — например `Europe/Moscow`

### 3. Запуск

```bash
docker compose up --build -d
docker compose logs -f bot
```

Остановка:

```bash
docker compose down
```

Данные Postgres лежат в volume `postgres_data` и не пропадают при `down`.

## Локальный запуск без Docker (опционально)

Нужен свой Postgres и Python 3.12+.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt
# в .env укажи POSTGRES_HOST=localhost
python -m bot.main
```

## Структура

```
bot/
  config.py          # env / settings
  main.py            # точка входа
  db/                # модели и сессия
  handlers/          # команды
  middlewares/       # whitelist доступа
  services/          # планировщик напоминаний
  keyboards/         # кнопки
docker-compose.yml   # bot + postgres
Dockerfile
.env.example
```

## Безопасность

- `.env` в `.gitignore` — не коммить токены и пароли
- В бота пускаются только люди из `FAMILY_MEMBERS`
- В репозитории только `.env.example` с плейсхолдерами
=======
# family_bot
Полезный бот для тех кто забывает дни рождения родственников и что нужно было купить
>>>>>>> d510b09b1cc002a5a46c46ee4bf27acd254e9af1
