from aiogram import types, F, Router, html
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from netschoolapi import NetSchoolAPI

from handlers import database, files, keyboards, get_time, login
from handlers.fsm import *



router = Router(name=__name__)
db = database.DB()


@router.message(F.text.lower() == files.get_settings()["buttons"]["reply"]["time"].lower())
async def time_handler(msg: Message):
    ns = await login.ns_login(tg_username=msg.from_user.username)
    
    s = await get_time.generate_time_str(ns)
    
    await msg.answer(s)