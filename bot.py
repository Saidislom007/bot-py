from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio

API_TOKEN = "8442391003:AAHL8WA8oqSqwVQvsa_YYZ2dxqiZYBWMoCk"  # Bu yerga bot tokeningizni qo'ying

# FSM orqali savol holatini saqlash uchun
class QuizStates(StatesGroup):
    Q1 = State()
    Q2 = State()
    Q3 = State()
    Finished = State()

# Savollar va javoblar ro'yxati
quiz_data = [
    {
        "question": "Python nima?",
        "options": ["Dasturlash tili", "Ovqat", "Film", "Mashina"],
        "correct": 0
    },
    {
        "question": "HTML nima?",
        "options": ["Dasturlash tili", "Markup tili", "Musika janri", "Sport turi"],
        "correct": 1
    },
    {
        "question": "AI ning to'liq nomi nima?",
        "options": ["Artificial Intelligence", "Amazing Idea", "Apple Inc.", "Auto Industry"],
        "correct": 0
    },
]

# Bot va Dispatcher yaratish
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Inline tugmalar yaratish funksiyasi
def create_options(options):
    # Har bir tugmani alohida qatorga joylaymiz
    buttons = [[types.InlineKeyboardButton(text=opt, callback_data=str(i))] for i, opt in enumerate(options)]
    kb = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb

# /start komanda handler
@dp.message(Command(commands=["start"]))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("Salom! Test boshlaymiz. Birinchi savol:")
    await state.update_data(score=0)
    await send_question(message.chat.id, 0, state)

# Savolni yuborish funksiyasi
async def send_question(chat_id, q_index, state: FSMContext):
    if q_index >= len(quiz_data):
        data = await state.get_data()
        score = data.get("score", 0)
        await bot.send_message(chat_id, f"Test tugadi! Siz {score}/{len(quiz_data)} to'g'ri javob berdingiz.")
        await state.clear()
        return

    question = quiz_data[q_index]["question"]
    options = quiz_data[q_index]["options"]
    kb = create_options(options)

    await bot.send_message(chat_id, f"{question}", reply_markup=kb)
    
    # FSM holatini yangilash
    if q_index == 0:
        await state.set_state(QuizStates.Q1)
    elif q_index == 1:
        await state.set_state(QuizStates.Q2)
    elif q_index == 2:
        await state.set_state(QuizStates.Q3)

# Inline tugma handler
@dp.callback_query()
async def handle_answer(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    score = data.get("score", 0)
    
    # Qaysi savol hozirgi holatda
    current_state = await state.get_state()
    if current_state == QuizStates.Q1.state:
        q_index = 0
    elif current_state == QuizStates.Q2.state:
        q_index = 1
    elif current_state == QuizStates.Q3.state:
        q_index = 2
    else:
        await callback.message.edit_text("Test tugagan yoki xatolik yuz berdi!")
        return

    selected_option = int(callback.data)
    correct_option = quiz_data[q_index]["correct"]

    if selected_option == correct_option:
        score += 1
        await state.update_data(score=score)
        await callback.answer("To'g'ri ✅")
    else:
        await callback.answer(f"Noto'g'ri ❌. To'g'ri javob: {quiz_data[q_index]['options'][correct_option]}")

    # Keyingi savolga o'tish
    await send_question(callback.message.chat.id, q_index + 1, state)
    await callback.message.delete()

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
