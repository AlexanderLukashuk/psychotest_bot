from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.services.gemini_service import send_to_gemini_async
from database.mongo_client import tests_collection
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

router = Router()


class PassTest(StatesGroup):
    choosing_test = State()
    answering_question = State()


@router.message(Command("start_test"))
async def start_test(message: types.Message, state: FSMContext):
    tests = list(tests_collection.find({}, {"title": 1}))
    if not tests:
        await message.answer("Пока нет доступных тестов.")
        return

    buttons = [[KeyboardButton(text=test["title"])] for test in tests]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

    await message.answer("Выбери тест, который хочешь пройти:", reply_markup=keyboard)
    await state.set_state(PassTest.choosing_test)


@router.message(PassTest.choosing_test)
async def choose_test(message: types.Message, state: FSMContext):
    test = tests_collection.find_one({"title": message.text})
    if not test:
        await message.answer("Пожалуйста, выбери тест из списка кнопок.")
        return

    await state.update_data(
        test=test,
        current_question_index=0,
        user_answers=[]
    )

    await ask_next_question(message, state)


async def ask_next_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    test = data["test"]
    index = data["current_question_index"]

    if index >= len(test["questions"]):
        await finish_test(message, state)
        return

    question = test["questions"][index]
    buttons = [[KeyboardButton(text=option)] for option in question["options"]]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

    await message.answer(f"{question['question']}", reply_markup=keyboard)
    await state.set_state(PassTest.answering_question)


@router.message(PassTest.answering_question)
async def handle_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    test = data["test"]
    index = data["current_question_index"]
    question = test["questions"][index]

    if message.text not in question["options"]:
        await message.answer("Пожалуйста, выбери вариант из кнопок.")
        return

    user_answers = data["user_answers"]
    user_answers.append({
        "question": question["question"],
        "selected_option": message.text
    })

    await state.update_data(
        user_answers=user_answers,
        current_question_index=index + 1
    )

    await ask_next_question(message, state)


async def finish_test(message: types.Message, state: FSMContext):
    data = await state.get_data()
    test = data["test"]
    user_answers = data["user_answers"]

    result_text = "Тест завершён!\n\nВаши ответы:\n\n"
    for answer in user_answers:
        result_text += f"🔸 {answer['question']}\n➡️ {answer['selected_option']}\n\n"

    await message.answer(result_text, reply_markup=ReplyKeyboardRemove())

    # Отправка в Gemini API
    gemini_result = await send_to_gemini_async(test, user_answers)
    print(gemini_result)

    await message.answer(f"🧠 Результат от Gemini:\n\n{gemini_result}", reply_markup=ReplyKeyboardRemove())

    await state.clear()
