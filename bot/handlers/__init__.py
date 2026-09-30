from aiogram import Router

from bot.handlers import dates, notes, reminders, shopping, start


def setup_routers() -> Router:
    root = Router(name="root")
    root.include_router(start.router)
    root.include_router(shopping.router)
    root.include_router(notes.router)
    root.include_router(dates.router)
    root.include_router(reminders.router)
    return root
