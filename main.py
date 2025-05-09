import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from bot.handlers import common, test_creation, test_deleting, test_passing


async def main():
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(common.router)
    dp.include_router(test_creation.router)
    dp.include_router(test_passing.router)
    dp.include_router(test_deleting.router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
