from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import ALLOWED_CREATORS
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from database.mongo_client import tests_collection

router = Router()

# Машина состояний


class CreateTest(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_question = State()
    waiting_for_option = State()
    confirming_add_more_options = State()
    confirming_add_more_questions = State()
    waiting_for_scoring_logic = State()

# Команда для старта создания теста


@router.message(Command("create_test"))
async def cmd_create_test(message: types.Message, state: FSMContext):
    if message.from_user.username not in ALLOWED_CREATORS:
        await message.answer("Извините, у вас нет прав для создания тестов.")
        return

    await message.answer("Введите название вашего психологического теста:")
    await state.set_state(CreateTest.waiting_for_title)


