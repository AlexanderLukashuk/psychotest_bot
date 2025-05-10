# import asyncio
# from fastapi import FastAPI, Request
# from aiogram import Bot, Dispatcher
# from aiogram.types import Update
# from config import BOT_TOKEN
# from bot.handlers import common, test_creation, test_deleting, test_passing

# app = FastAPI()

# bot = Bot(BOT_TOKEN)
# dp = Dispatcher()

# dp.include_router(common.router)
# dp.include_router(test_creation.router)
# dp.include_router(test_passing.router)
# dp.include_router(test_deleting.router)

# @app.post("/webhook")
# async def telegram_webhook(req: Request):
#     data = await req.json()
#     update = Update.model_validate(data)
#     await dp.feed_update(bot, update)
#     return {"status": "ok"}

# @app.on_event("startup")
# async def on_startup():
#     # Устанавливаем webhook на Vercel URL
#     # webhook_url = "https://psychotest-bot.vercel.app/webhook"
#     webhook_url = "https://psychotest-bot.fly.dev/webhook"
#     await bot.set_webhook(webhook_url)

# @app.on_event("shutdown")
# async def on_shutdown():
#     await bot.delete_webhook()
