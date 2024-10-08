from aiogram import types, F, Router, html
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from netschoolapi import NetSchoolAPI

from handlers import database, files, keyboards, calendar
from handlers.login import ns_login
from handlers.fsm import *

from typing import Callable, Any



router = Router(name=__name__)
db = database.DB()


def format_template(title: str, period: Any) -> str:
    settings = files.get_settings()["txt"]
    
    if len(list(period)) == 1:
        return settings["slider_header_day"].format(
            title,
            period
        )
    elif isinstance(period[-1], int):
        return settings["slider_header_week"].format(
            title,
            *period
        )
    else:
        return settings["slider_header_cycle"].format(
            title,
            *period
        )
    


# @router.message()
async def new_slider(msg: Message,
                     state: FSMContext,
                     title: str,
                     obj_func: Callable,
                     period_func: Callable):
    
    ns = await ns_login(tg_username=msg.from_user.username)
    
    if ns:
        period = await period_func(ns)
        
        template = format_template(title, period)
        kb = keyboards.get_inline("slider")
        
        bot_msg = await msg.answer(
            text=template,
            reply_markup=kb
        )
        
        await state.set_data({
            SliderFSM.msg: bot_msg,
            SliderFSM.title: title,
            SliderFSM.obj_func: obj_func,
            SliderFSM.period_func: period_func,
            SliderFSM.period: 0,
            SliderFSM.ns: ns
        })
    else:
        err = files.get_settings()["txt"]["connection_error"]
        
        await msg.answer(err)


# Изменение периода
@router.callback_query(F.data.split(" ")[0] == "slider_move")
async def slider_move_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    bot_msg = data[SliderFSM.msg]
    title = data[SliderFSM.title]
    period_func = data[SliderFSM.period_func]
    period_n = data[SliderFSM.period]
    ns = data[SliderFSM.ns]
    
    period_n += int(callback.data.split(" ")[-1])
    
    new_period = await period_func(ns, period_n)
    
    template = format_template(title, new_period)
    kb = keyboards.get_inline("slider")
    
    bot_msg = await bot_msg.edit_text(
        text=template,
        reply_markup=kb
    )
    
    await state.update_data({
        SliderFSM.msg: bot_msg,
        SliderFSM.period: period_n,
    })