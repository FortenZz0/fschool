from aiogram import types, F, Router, html
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from netschoolapi import NetSchoolAPI

from handlers import database, files, keyboards
from handlers.fsm import *

from .login_router import get_admin, get_user, start_login_handler



router = Router(name=__name__)
ACTIVE = True
db = database.DB()


@router.message()
async def message_handler(msg: Message):
    await msg.answer('Hello from my router!')