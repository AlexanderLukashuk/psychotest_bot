from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import ALLOWED_CREATORS
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from database.mongo_client import tests_collection

router = Router()


class CreateTest(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_question = State()
    waiting_for_option = State()
    confirming_add_more_options = State()
    confirming_add_more_questions = State()
    waiting_for_scoring_logic = State()


@router.message(Command("create_test"))
async def cmd_create_test(message: types.Message, state: FSMContext):
    if message.from_user.username not in ALLOWED_CREATORS:
        await message.answer("Извините, у вас нет прав для создания тестов.")
        return

    await message.answer("Введите название вашего психологического теста:")
    await state.set_state(CreateTest.waiting_for_title)


@router.message(CreateTest.waiting_for_title)
async def process_test_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Теперь введите описание/инструкцию теста.")
    await state.set_state(CreateTest.waiting_for_description)


@router.message(CreateTest.waiting_for_description)
async def process_test_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Отлично! Теперь введите первый вопрос теста.")
    await state.set_state(CreateTest.waiting_for_question)


@router.message(CreateTest.waiting_for_question)
async def process_test_question(message: types.Message, state: FSMContext):
    await state.update_data(current_question=message.text, options=[])
    await message.answer("Теперь введите вариант ответа для этого вопроса:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(CreateTest.waiting_for_option)


@router.message(CreateTest.waiting_for_option)
async def process_option(message: types.Message, state: FSMContext):
    data = await state.get_data()
    options = data.get("options", [])
    options.append(message.text)
    await state.update_data(options=options)

    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Добавить ещё вариант")],
        [KeyboardButton(text="Закончить ввод вариантов")]
    ], resize_keyboard=True)

    await message.answer("Вариант сохранён. Что дальше?", reply_markup=keyboard)
    await state.set_state(CreateTest.confirming_add_more_options)


@router.message(CreateTest.confirming_add_more_options)
async def confirm_add_option(message: types.Message, state: FSMContext):
    if message.text == "Добавить ещё вариант":
        await message.answer("Введите следующий вариант ответа:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(CreateTest.waiting_for_option)

    elif message.text == "Закончить ввод вариантов":
        data = await state.get_data()
        question = data["current_question"]
        options = data["options"]

        questions = data.get("questions", [])

        questions.append({
            "question": question,
            "options": options
        })

        await state.update_data(questions=questions)

        keyboard = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="Добавить ещё вопрос")],
            [KeyboardButton(text="Завершить создание теста")]
        ], resize_keyboard=True)

        await message.answer(f"Вопрос добавлен.\nЧто дальше?", reply_markup=keyboard)
        await state.set_state(CreateTest.confirming_add_more_questions)

    else:
        await message.answer("Пожалуйста, выбери вариант из кнопок.")


@router.message(CreateTest.confirming_add_more_questions)
async def confirm_add_question(message: types.Message, state: FSMContext):
    if message.text == "Добавить ещё вопрос":
        await message.answer("Введите текст следующего вопроса:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(CreateTest.waiting_for_question)

    elif message.text == "Завершить создание теста":
        await message.answer("Отлично, теперь введи команду /done_questions чтобы добавить логику оценки и завершить создание теста.", reply_markup=ReplyKeyboardRemove())
        await state.set_state(None)

    else:
        await message.answer("Пожалуйста, выбери вариант из кнопок.")


@router.message(Command("done_questions"))
async def done_questions(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if "questions" not in data or len(data["questions"]) == 0:
        await message.answer("Вы ещё не добавили ни одного вопроса.")
        return

    await message.answer(
        "Теперь укажите логику оценки результатов.\n\n"
        "Введите максимально подробно и в деталях как должны оцениваться результаты\n"
    )
    await state.set_state(CreateTest.waiting_for_scoring_logic)


@router.message(CreateTest.waiting_for_scoring_logic)
async def process_scoring_logic(message: types.Message, state: FSMContext):
    logic_text = message.text
    data = await state.get_data()

    test_document = {
        "title": data["title"],
        "title_lower": data["title"].lower(),
        "description": data["description"],
        "questions": data["questions"],
        "scoring_logic": logic_text,
        "creator_username": message.from_user.username
    }

    tests_collection.insert_one(test_document)

    await message.answer(f"Тест \"{data['title']}\" успешно сохранён ✅")
    await state.clear()
