from aiogram import types, F, Router
from aiogram.types import Message
from aiogram.filters import Command

from datetime import datetime, date, time
from netschoolapi import NetSchoolAPI

from handlers import time_handler as time_h
from handlers import days_handler as days_h
from handlers import diary_handler as diary_h
from handlers import output_handler as out_h
from handlers import marks_handler as marks_h



router = Router()


@router.message(Command("start"))
async def start_handler(msg: Message):
    await msg.answer("Hello world!")


@router.message()
async def message_handler(msg: Message):
    await msg.answer(f"Твой ID: {msg.from_user.id}")