from aiogram import types, F, Router, html
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from netschoolapi import NetSchoolAPI

from handlers import database, files, keyboards, calendar
from handlers.login import ns_login, get_user
from handlers.fsm import *

from typing import Callable, Any
from datetime import date

from handlers.schemas import MyDiary



router = Router(name=__name__)
db = database.DB()


def format_template(title: str, period: Any) -> str:
    settings = files.get_settings()
    
    x = "на" if title == settings["buttons"]["reply"]["diary"] else "за"
    
    if period[0] == period[1]:
        return settings["txt"]["slider_header_day"].format(
            title,
            x,
            *period[1:]
        )
    elif isinstance(period[-1], int):
        return settings["txt"]["slider_header_week"].format(
            title,
            x,
            *period
        )
    else:
        return settings["txt"]["slider_header_cycle"].format(
            title,
            x,
            *period
        )
    

async def create_slider(msg: Message,
                        state: FSMContext,
                        title: str,
                        obj_func: Callable):
    settings = files.get_settings()
    
    await state.set_data({
        SliderFSM.title: title,
        SliderFSM.obj_func: obj_func,
        SliderFSM.cache: {}
    })
    
    await start_get_period(msg, state, title, title == settings["buttons"]["reply"]["diary"])


async def start_get_period(msg: Message, state: FSMContext, title: str, is_short: bool = False):
    template = files.get_settings()["txt"]["get_period"]
    
    kb_name = "period_short" if is_short else "period"
    kb = keyboards.get_inline(kb_name)
    
    bot_msg = await msg.answer(
        text=template.format(title),
        reply_markup=kb
    )
    
    await state.update_data({SliderFSM.msg: bot_msg})
    

@router.callback_query(F.data.split(" ")[0] == "period")
async def get_period_func_handler(callback: CallbackQuery, state: FSMContext):
    user_period = get_user(callback.from_user.username)[5]
    
    period_funcs = {
        "day": calendar.get_day,
        "week": calendar.get_week,
        "cycle": lambda ns, add_cycles: calendar.get_cycle(ns, user_period, add_cycles)
    }
    
    period = callback.data.split(" ")[1]
    
    await state.update_data({
        SliderFSM.period_func: period_funcs[period]
    })
    
    await new_slider(state)
    

# @router.message()
async def new_slider(state: FSMContext):
    data = await state.get_data()
    bot_msg = data[SliderFSM.msg]
    period_func = data[SliderFSM.period_func]
    title = data[SliderFSM.title]
    # obj_func = data[SliderFSM.obj_func]
    
    ns = await ns_login(tg_username=bot_msg.chat.username)
    
    if ns:
        period = await period_func(ns, 0)
        
        template = format_template(title, period)
        
        kb_name = "slider" if period[0] == period[1] else "slider_cycle"
        kb = keyboards.get_inline(kb_name)
        
        bot_msg = await bot_msg.edit_text(
            text=template,
            reply_markup=kb
        )
        
        await state.update_data({
            SliderFSM.msg: bot_msg,
            SliderFSM.period_n: 0,
            SliderFSM.period_title: str(period[-1]),
            SliderFSM.ns: ns
        })
    else:
        err = files.get_settings()["txt"]["connection_error"]
        
        await bot_msg.edit_text(text=err)



# Изменение периода
@router.callback_query(F.data.split(" ")[0] == "slider_move")
async def slider_move_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    bot_msg = data[SliderFSM.msg]
    title = data[SliderFSM.title]
    period_func = data[SliderFSM.period_func]
    period_n = data[SliderFSM.period_n]
    ns = data[SliderFSM.ns]
    
    period_n += int(callback.data.split(" ")[-1])
    new_period = await period_func(ns, period_n)
    
    template = format_template(title, new_period)
    
    kb_name = "slider" if new_period[0] == new_period[1] else "slider_cycle"
    kb = keyboards.get_inline(kb_name)
    
    bot_msg = await bot_msg.edit_text(
        text=template,
        reply_markup=kb
    )
    
    await state.update_data({
        SliderFSM.msg: bot_msg,
        SliderFSM.period_n: period_n,
        SliderFSM.period_title: str(new_period[-1])
    })
    

# Загрузка данных из слайдера
@router.callback_query(F.data == "slider_load")
async def slider_load_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    bot_msg = data[SliderFSM.msg]
    period_func = data[SliderFSM.period_func]
    period_n = data[SliderFSM.period_n]
    period_title = data[SliderFSM.period_title]
    ns = data[SliderFSM.ns]
    obj_func = data[SliderFSM.obj_func]
    cache = data[SliderFSM.cache]
    
    obj = cache.get(period_n, None)
    files = []
    
    if not obj:
        period = await period_func(ns, period_n)
        obj = await obj_func(ns, period[0], period[1], period_title)
        
        cache[period_n] = str(obj)
        await state.update_data({SliderFSM.cache: cache})
        
        if isinstance(obj, MyDiary):
            attachments = await obj.get_attachments(ns)
            
            for att in attachments:
                buffer = await att.download(ns)
                f = BufferedInputFile(buffer.getvalue(), att.fname)
                files.append(f)
    
    if bot_msg.html_text != str(obj) and obj:
        bot_msg = await bot_msg.edit_text(
            text=str(obj),
            reply_markup=bot_msg.reply_markup
        )
        
        for f in files:
            await bot_msg.answer_document(f)
        
        await state.update_data({SliderFSM.msg: bot_msg})