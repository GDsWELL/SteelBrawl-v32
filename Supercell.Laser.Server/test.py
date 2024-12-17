from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = 'tokentoken' # Замените на свой токен бота

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=1)
    url_button = InlineKeyboardButton('Сайт', url='https://steelbrawl.ru') # Замените на ваш сайт
    keyboard.add(url_button)
    await message.answer('Привет! 👋', reply_markup=keyboard)

@dp.message_handler()
async def handle_default(message: types.Message):
    if message.chat.type == types.ChatType.GROUP or message.chat.type == types.ChatType.SUPERGROUP:
        await message.answer("Данный бот находится в чате, перейдите ко мне в сообщения чтобы взаимодействовать.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)