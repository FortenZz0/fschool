from aiogram import types, F, Router, html
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from netschoolapi import NetSchoolAPI
import requests

from handlers import database, files, keyboards
from handlers.fsm import *

from .login_router import get_admin, get_user, start_login_handler



router = Router(name=__name__)
db = database.DB()


@router.message(F.text.lower() == files.get_settings()["buttons"]["reply"]["gotons"].lower())
async def gotons_handler(msg: Message):
    user = get_user(msg.from_user.username)
    
    settings = files.get_settings()
    txt = settings["txt"]
    
    if not user:
        await msg.answer(txt["gotons_error"])
        return
    
    url = settings["values"]["gotons_url_template"].format(user[1])
    
    await msg.answer(
        txt["gotons_template"].format(
            user[4],
            user[2],
            user[3],
            url
        ),
        reply_markup=keyboards.get_inline("gotons", data=[url])
    )