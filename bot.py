import asyncio

from aiogram import Bot, Dispatcher
from aiogram_dialog.setup import setup_dialogs

from config import settings
from handlers.main import router as main_router
from handlers.tasks import router as task_router

token = settings.BOT_TOKEN
bot = Bot(token=token)
dispatcher = Dispatcher()
dispatcher.include_router(main_router)
dispatcher.include_router(task_router)


async def main():
    setup_dialogs(dispatcher)
    await bot.delete_webhook(drop_pending_updates=True)
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    while True:
        try:
            asyncio.run(main())
        except Exception:
            pass
