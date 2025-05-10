from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from config import ALLOWED_CREATORS

from database.mongo_client import tests_collection

router = Router()


class DeleteTest(StatesGroup):
    waiting_for_test_name = State()


@router.message(Command("delete_test"))
async def delete_test_command(message: types.Message, state: FSMContext):
    if message.from_user.username not in ALLOWED_CREATORS:
        await message.answer("Извините, у вас нет прав для создания тестов.")
        return


    tests = list(tests_collection.find({}, {"title": 1, "_id": 0}))
    if not tests:
        await message.answer("В базе нет доступных тестов.")
        return

    test_titles = "\n".join(f"- {test['title']}" for test in tests)
    await message.answer(f"Список доступных тестов:\n\n{test_titles}\n\nОтправь название теста, который хочешь удалить:")
    await state.set_state(DeleteTest.waiting_for_test_name)


@router.message(DeleteTest.waiting_for_test_name)
async def handle_test_deletion(message: types.Message, state: FSMContext):
    test_name = message.text.lower()

    result = tests_collection.delete_one({"title_lower": test_name})

    if result.deleted_count == 1:
        await message.answer(f"Тест '{message.text}' успешно удалён ✅")
    else:
        await message.answer(f"Тест с названием '{message.text}' не найден ❌")

    await state.clear()
