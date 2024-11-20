from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import asyncio

api = ""
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

ikb = InlineKeyboardMarkup()
button = InlineKeyboardButton(text='Рассчитать норму калорий',
                              callback_data='calories')
button2 = InlineKeyboardButton(text='Формулы расчёта',
                              callback_data='formulas')
ikb.add(button)
ikb.add(button2)

start_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Info')],
        [
            KeyboardButton(text='shop'),
            KeyboardButton(text='donate')
        ]
    ], resize_keyboard=True
)


@dp.message_handler(text=['Рассчитать'])
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=ikb)

@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('Формула рассчета для мужчин: '
                              '10 х вес (кг) + 6,25 x рост (см)'
                              ' – 5 х возраст (г) + 5')
    await call.message.answer('Формула рассчета для женщин: '
                              '10 x вес (кг) + 6,25 x рост (см)'
                              ' – 5 x возраст (г) – 161')
    await call.answer()

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button = KeyboardButton(text="Рассчитать")
button2 = KeyboardButton(text="Информация")
kb.add(button)
kb.add(button2)

@dp.message_handler(commands='start')
async def start_message(message):
    await message.answer('Привет! Я бот помогающий Вашему здоровью.', reply_markup=kb)

@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()

@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer(f'Введите свой рост:')
    await UserState.growth.set()

@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer(f'Введите свой вес:')
    await UserState.weight.set()

@dp.message_handler(state=UserState.weight)
async def fsm_handler(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()

    try:
        age = float(data['age'])
        weight = float(data['weight'])
        growth = float(data['growth'])
    except:
        await message.answer(f'Не могу конвертировать введенные значения в числа.')
        await state.finish()
        return

    # Упрощенный вариант формулы Миффлина-Сан Жеора:
    # для мужчин: 10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5
    calories_man = 10 * weight + 6.25 * growth - 5 * age + 5
    # для женщин: 10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161
    calories_wom = 10 * weight + 6.25 * growth - 5 * age - 161
    await message.answer(f'Суточная норма калорий для мужчины: {calories_man} ккал')
    await message.answer(f'Суточная норма калорий для женщины: {calories_wom} ккал')
    await state.finish()

@dp.message_handler()

async def all_message(message):
    await message.answer('Привет!')
    await message.answer('Введите команду /start, чтобы начать общение.')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
    