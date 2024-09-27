import asyncio
import logging

from dotenv import find_dotenv, load_dotenv
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

# from routers import main_router
from routers import routers


denv = find_dotenv()
load_dotenv(denv)


async def main():
    bot = Bot(token=getenv("BOT_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    dp = Dispatcher(storage=MemoryStorage())
    
    for router in routers:
        dp.include_router(router)
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

