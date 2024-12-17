# -*- coding: cp1251 -*-


import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.dispatcher.filters import Command
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import logging

# Логирование
logging.basicConfig(level=logging.INFO)

API_TOKEN = '8069062516:AAH7E3M-3-W5UrPNnKAkKfDLdoGQ23saEag'
USER_ID = '6744773692'
FILE_PATH = 'bin/Debug/net6.0/battles.txt'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())  # Логирование ошибок и запросов

last_line_number = 0  # Номер последней обработанной строки

async def check_battles():
    global last_line_number
    if not os.path.isfile(FILE_PATH):
        logging.warning(f"Файл {FILE_PATH} не найден.")
        return

    with open(FILE_PATH, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        new_lines = lines[last_line_number:]
        for line in new_lines:
            if "ended battle!" in line:
                parts = line.split(' in ')
                if len(parts) > 1:
                    time_str = parts[1].split('s')[0].strip()
                    try:
                        battle_time = float(time_str)
                        if "gamemode: BattleRoyale" in line:
                            rank_str = line.split('Battle Rank: ')[-1].split(' ')[0]
                            rank = int(rank_str)
                            if rank < 2 and battle_time < 30:
                                message = f"Есть подозрение на читы! {line.strip()}"
                                await bot.send_message(chat_id=USER_ID, text=message)
                        elif "gamemode: BattleRoyaleTeam" in line:
                            rank_str = line.split('Battle Rank: ')[-1].split(' ')[0]
                            rank = int(rank_str)
                            if rank < 2 and battle_time < 30:
                                message = f"Есть подозрение на читы! {line.strip()}"
                                await bot.send_message(chat_id=USER_ID, text=message)
                        else:
                            if battle_time < 25:
                                message = f"Есть подозрение на читы! {line.strip()}"
                                await bot.send_message(chat_id=USER_ID, text=message)
                    except ValueError:
                        logging.error("Ошибка обработки строки", exc_info=True)
                        pass
        last_line_number = len(lines)

async def periodic_check():
    while True:
        await check_battles()
        await asyncio.sleep(20)  # Проверка каждые 20 секунд

# Обработчик команды /start
@dp.message_handler(Command('start'))
async def start_handler(message: types.Message):
    await message.reply("Привет! Я отслеживаю подозрительные логи. Начинаю работу...")
    logging.info("Бот начал отслеживать логи.")

# Запуск периодической проверки в фоне
async def on_startup(_):
    logging.info("Бот запущен и готов к работе!")
    asyncio.create_task(periodic_check())

# Основной запуск бота
if __name__ == '__main__':
    try:
        logging.info("Запуск бота...")
        executor.start_polling(dp, on_startup=on_startup)
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")
