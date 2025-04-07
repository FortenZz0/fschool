from aiogram import types, F, Router, html
from aiogram.types import Message, CallbackQuery
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
async def gotons_handler(msg: Message, state: FSMContext):
    user = get_user(msg.from_user.username)
    
    settings = files.get_settings()
    txt = settings["txt"]
    
    if not user:
        await msg.answer(txt["gotons_error"])
        return
    
    url = settings["values"]["gotons_url_template"].format(user[1])
    
    bot_msg = await msg.answer(
        txt["gotons_template"].format(
            user[4],
            user[2],
            user[3],
            url
        ),
        reply_markup=keyboards.get_inline("gotons", data=[url])
    )
    
    await state.update_data({
        GotonsFSM.bot_msg: bot_msg,
        GotonsFSM.user_msg: msg
    })
    

@router.callback_query(F.data.split(" ")[0] == "gotons_del")
async def gotons_del_handler(callback: CallbackQuery, state: FSMContext):
    fsm_data = await state.get_data()
    
    bot_msg = fsm_data[GotonsFSM.bot_msg]
    user_msg = fsm_data[GotonsFSM.user_msg]
    
    await bot_msg.delete()
    await user_msg.delete()
    