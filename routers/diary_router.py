from aiogram import types, F, Router, html
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from netschoolapi import NetSchoolAPI

from handlers import database, files, keyboards, diary, calendar
from handlers.fsm import *

from routers.slider_router import create_slider



router = Router(name=__name__)
db = database.DB()


@router.message(F.text.lower() == files.get_settings()["buttons"]["reply"]["diary"].lower())
async def diary_handler(msg: Message, state: FSMContext):
    txt = files.get_settings()["buttons"]["reply"]["diary"]
    
    await create_slider(
        msg,
        state,
        txt,
        diary.get_diary
    )