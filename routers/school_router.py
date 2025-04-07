from aiogram import types, F, Router, html
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from netschoolapi import NetSchoolAPI

from handlers import database, files, keyboards
from handlers.fsm import *

from .login_router import ns_login



router = Router(name=__name__)
ACTIVE = True
db = database.DB()


@router.message(F.text.lower() == files.get_settings()["buttons"]["reply"]["school"].lower())
async def school_handler(msg: Message) -> None:
    ns = await ns_login(tg_username=msg.from_user.username)
    txt = files.get_settings()["txt"]
    
    if ns is None:
        await msg.answer(txt["connection_error"])
        return
    
    school = await ns.school()
    
    await msg.answer(txt["school_info"].format(
        school.name,
        ns._school_id,
        school.address,
        school.about,
        school.email,
        school.site,
        school.phone,
        school.director,
        school.AHC,
        school.IT,
        school.UVR
    ))
    
    await ns.logout()