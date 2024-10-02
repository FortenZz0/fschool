from aiogram import types, F, Router, html
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from netschoolapi import NetSchoolAPI

from handlers import database, files, keyboards
from handlers.fsm import *

from .login_router import get_admin, get_user, start_login_handler


router = Router(name=__name__)


# Обработка команды /start
@router.message(Command("start"))
async def start_handler(msg: Message, state: FSMContext):
    settings = files.get_settings()
    
    username = msg.from_user.username
    
    kb = None
    if get_user(username):
        kb = keyboards.get_reply("main", bool(get_admin(username))) 
    
    await msg.answer(
        settings["txt"]["start"],
        reply_markup=kb
    )
    
    print(123)
    await start_login_handler(msg, state)