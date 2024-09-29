from aiogram import types, F, Router, html
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from netschoolapi import NetSchoolAPI

from handlers import database, files, keyboards
from handlers.fsm import *



router = Router(name=__name__)
db = database.DB()


@router.message()
async def message_handler(msg: Message):
    await msg.answer('Hello from my router!')