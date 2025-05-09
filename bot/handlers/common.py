from aiogram import Router, F
from aiogram.types import Message
from config import ALLOWED_CREATORS

router = Router()

@router.message(F.text == "/start")
async def start_command(message: Message):
    if message.from_user.username in ALLOWED_CREATORS:
        await message.answer("Привет, создатель тестов! Готов начать создавать?")
    else:
        await message.answer("Привет! Ты можешь пройти психологические тесты. Напиши /tests чтобы посмотреть доступные.")
