from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher import FSMContext, filters
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup
from database import get_all_categories, add_spending, add_user, add_categories, month_data, \
    get_users_category_summary_in_this_month, get_category_summary_spending_in_this_month
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import datetime
from setting import API_TOKEN


bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Spending(StatesGroup):
    categories = State()
    spending = State()


def create_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    categories = get_all_categories()
    for category in categories:
        button = InlineKeyboardMarkup(text=f'{category}')
        keyboard.add(button)

    return keyboard


@dp.message_handler(commands=['допомога', 'help'])
async def help_command(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button = InlineKeyboardMarkup(text=f'/add_user')
    button1 = InlineKeyboardMarkup(text=f'/місяць')
    button2 = InlineKeyboardMarkup(text=f'/витрати')

    keyboard.add(button, button1, button2)

    await message.answer('Поки є такі команди - add_user -додає користувача, тобто вас та add_category - додає нову '
                         'категорію, для того щоб додати категорію, введіть цю команду та через пробіл введіть нову '
                         'категорію', reply_markup=keyboard)


@dp.message_handler(commands=['витрати'])
async def all_day(message: types.Message):
    data = get_users_category_summary_in_this_month()
    answer = ''
    for key in data.keys():
        if answer != '':
            answer += '\n'
        answer += str(key) + ' число:\n'
        for data_one in data[key]:
            answer += data_one + '\n'
    await message.answer(answer)


@dp.message_handler(commands=['місяць'])
async def month(message: types.Message):
    data = get_category_summary_spending_in_this_month()
    answer = ''
    for word in data:
        answer += word + '\n'
    await message.answer(answer)


@dp.message_handler(commands=['add_user'])
async def telegram_add_user(message: types.Message):
    answer_text = add_user(message.chat.first_name, message.from_id, message.chat.username)

    await message.answer(answer_text)


@dp.message_handler(commands=['add_categories'])
async def telegram_add_category(message: types.Message):
    answer_text = add_categories(message.text[16:])

    await message.answer(answer_text)


@dp.message_handler()
async def start(message: types.Message):
    await message.answer("Введіть суму затрат:")
    await Spending.spending.set()


@dp.message_handler(lambda message: message.text.isdigit(), state=Spending.spending)
async def process_spending(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['spending'] = int(message.text)
    categories_keyboard = create_keyboard()
    await message.answer(f"Сума затрат: {data['spending']} грн\nВиберіть категорію:", reply_markup=categories_keyboard)
    await Spending.categories.set()


@dp.message_handler(lambda message: not message.text.isdigit(), state=Spending.spending)
async def process_invalid_input(message: types.Message):
    await message.answer("Будь ласка, введіть суму затрат, використовуючи цифри.")


@dp.message_handler(lambda message: message.text not in get_all_categories(), state=Spending.categories)
async def process_invalid_category(message: types.Message):
    categories_keyboard = create_keyboard()
    await message.answer("Будь ласка, виберіть категорію з клавіатури:", reply_markup=categories_keyboard)


@dp.message_handler(lambda message: message.text in get_all_categories(), state=Spending.categories)
async def process_category(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        spending = data['spending']
        category = message.text
        # Здесь вы можете сохранить категорию и сумму в базе данных
        # Например: save_to_database(category, spending)
        await message.answer(f"Затрати в категорії '{category}' на суму {spending} грн записано.")
        add_spending(category, spending, datetime.datetime.now(), message.chat.id)
    await state.finish()


def main():
    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    main()