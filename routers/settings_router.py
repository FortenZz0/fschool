from aiogram import types, F, Router, html
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from netschoolapi import NetSchoolAPI

from handlers import database, files, keyboards, callback
from handlers.fsm import *

from .login_router import start_login_handler



router = Router(name=__name__)
db = database.DB()


@router.message(F.text.lower() == files.get_settings()["buttons"]["reply"]["settings"].lower())
@router.callback_query(F.data == "settings_back")
async def settings_handler(msg: Message | CallbackQuery, state: FSMContext):
    settings = files.get_settings()
    
    cycle_translate = {
        "quarters": "четверть",
        "trimesters": "триместр",
        "half": "полугодие"
    }
        
    kb = keyboards.get_inline("settings_main")
    
    if isinstance(msg, Message):
        db.execute("SELECT cycle FROM users WHERE username = ?", (msg.from_user.username,))
        cycle = cycle_translate[db.fetchone()[0]]
        
        set_msg = await msg.answer(
            settings["txt"]["settings"].format(cycle),
            reply_markup=kb
        )
        
        await state.set_data({
            SettingsFSM.msg: set_msg,
            SettingsFSM.username: msg.from_user.username,
            SettingsFSM.cycle: cycle
        })
    else:
        cycle = (await state.get_data())[SettingsFSM.cycle]
        
        if cycle in list(cycle_translate.keys()):
            cycle = cycle_translate[cycle]
        
        await msg.message.edit_text(
            settings["txt"]["settings"].format(cycle),
            reply_markup=kb
        )
    
    
@router.callback_query(F.data == "edit_cycle")
async def edit_cycle_handler(callback: CallbackQuery):
    settings = files.get_settings()
    
    kb = keyboards.get_inline("edit_cycle")
    
    await callback.message.edit_text(
        settings["txt"]["settings_edit_cycle"],
        reply_markup=kb
    )
    
    
@router.callback_query(F.data.split(" ")[0] == "change_cycle")
async def edit_cycle_handler(callback: CallbackQuery, state: FSMContext):
    new_cycle = callback.data.split(" ")[-1]
    
    data = await state.get_data()
    username = data[SettingsFSM.username]
    
    db.execute(
        "UPDATE users SET cycle = ? WHERE username = ?",
        (new_cycle, username)
    )
    db.commit()
    
    await state.update_data({SettingsFSM.cycle: new_cycle})
    await settings_handler(callback, state)


@router.callback_query(F.data == "account_exit")
async def account_exit_handler(callback: CallbackQuery):
    settings = files.get_settings()
    
    kb = keyboards.get_inline("sure", prefix="exit")
    
    await callback.message.edit_text(
        settings["txt"]["exit_sure"],
        reply_markup=kb
    )


@router.callback_query(F.data.split(" ")[0] == "sure_exit")
async def edit_cycle_handler(callback: CallbackQuery, state: FSMContext):
    action = callback.data.split(" ")[-1]
    
    data = await state.get_data()
    username = data[SettingsFSM.username]
    
    if action == "yes":
        db.execute(
            "DELETE FROM users WHERE username = ?",
            (username,)
        )
        db.commit()
    
        await state.clear()
        await start_login_handler(callback.message, state, False, False)
    else:
        await settings_handler(callback, state)