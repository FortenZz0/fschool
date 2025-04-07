from aiogram import types, F, Router, html
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from netschoolapi import NetSchoolAPI

from handlers import database, files, keyboards, marks, diary, calendar
from handlers.fsm import *

from routers.slider_router import create_slider



router = Router(name=__name__)
ACTIVE = True
db = database.DB()


@router.message(F.text.lower() == files.get_settings()["buttons"]["reply"]["marks"].lower())
async def marks_handler(msg: Message, state: FSMContext):
    txt = files.get_settings()["buttons"]["reply"]["marks"]
    
    async def m(ns, start, end, period_title):
        d = await diary.get_diary(ns, start, end, "")
        return marks.get_marks(d, period_title)
    
    await create_slider(
        msg,
        state,
        txt,
        m
    )