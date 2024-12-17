# -*- coding: cp1251 -*-


import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.dispatcher.filters import Command
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import logging

# Ëîãèðîâàíèå
logging.basicConfig(level=logging.INFO)

API_TOKEN = 'токен бота'
USER_ID = 'тут ид юзера тг'
FILE_PATH = 'bin/Debug/net6.0/battles.txt'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())  # Ëîãèðîâàíèå îøèáîê è çàïðîñîâ

last_line_number = 0  

async def check_battles():
    global last_line_number
    if not os.path.isfile(FILE_PATH):
        logging.warning(f"Ôàéë {FILE_PATH} íå íàéäåí.")
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
                                message = f"Åñòü ïîäîçðåíèå íà ÷èòû! {line.strip()}"
                                await bot.send_message(chat_id=USER_ID, text=message)
                        elif "gamemode: BattleRoyaleTeam" in line:
                            rank_str = line.split('Battle Rank: ')[-1].split(' ')[0]
                            rank = int(rank_str)
                            if rank < 2 and battle_time < 30:
                                message = f"Åñòü ïîäîçðåíèå íà ÷èòû! {line.strip()}"
                                await bot.send_message(chat_id=USER_ID, text=message)
                        else:
                            if battle_time < 25:
                                message = f"Åñòü ïîäîçðåíèå íà ÷èòû! {line.strip()}"
                                await bot.send_message(chat_id=USER_ID, text=message)
                    except ValueError:
                        logging.error("Îøèáêà îáðàáîòêè ñòðîêè", exc_info=True)
                        pass
        last_line_number = len(lines)

async def periodic_check():
    while True:
        await check_battles()
        await asyncio.sleep(20)  # Ïðîâåðêà êàæäûå 20 ñåêóíä

# Îáðàáîò÷èê êîìàíäû /start
@dp.message_handler(Command('start'))
async def start_handler(message: types.Message):
    await message.reply("Ïðèâåò! ß îòñëåæèâàþ ïîäîçðèòåëüíûå ëîãè. Íà÷èíàþ ðàáîòó...")
    logging.info("Áîò íà÷àë îòñëåæèâàòü ëîãè.")

# Çàïóñê ïåðèîäè÷åñêîé ïðîâåðêè â ôîíå
async def on_startup(_):
    logging.info("Áîò çàïóùåí è ãîòîâ ê ðàáîòå!")
    asyncio.create_task(periodic_check())

# Îñíîâíîé çàïóñê áîòà
if __name__ == '__main__':
    try:
        logging.info("Çàïóñê áîòà...")
        executor.start_polling(dp, on_startup=on_startup)
    except Exception as e:
        logging.error(f"Îøèáêà ïðè çàïóñêå áîòà: {e}")
