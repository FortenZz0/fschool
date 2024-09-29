from aiogram import types, F, Router, html
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from netschoolapi import NetSchoolAPI

from handlers import database, files, keyboards
from handlers.fsm import *

from .login_router import get_admin, get_user



router = Router(name=__name__)
db = database.DB()


async def load_data(state: FSMContext) -> list[int, int]:
    db.execute("SELECT * FROM users")
    users = db.fetchall()
    
    db.execute("SELECT * FROM admins")
    admins = db.fetchall()
    
    await state.update_data({
        AdminFSM.users: users,
        AdminFSM.admins: admins  
    })
    
    return [len(users), len(admins)]


@router.message(F.text.lower() == files.get_settings()["buttons"]["reply"]["admin"].lower())
async def admin_handler(msg: Message, state: FSMContext, new_msg: bool = True):
    if new_msg:
        if not get_admin(msg.from_user.username):
            return
    
    settings = files.get_settings()
    
    data = await load_data(state)
    kb = keyboards.get_inline("admin_main", data)
    
    if new_msg:
        admin_msg = await msg.answer(
            settings["txt"]["admin_main"],
            reply_markup=kb
        )
    else:
        admin_msg = msg
        await msg.edit_text(
            settings["txt"]["admin_main"],
            reply_markup=kb
        )
    
    await state.update_data({
        AdminFSM.msg: admin_msg,
        AdminFSM.users_page_n: 0,
        AdminFSM.admins_page_n: 0
    })

    
@router.callback_query(F.data.split(" ")[0] == "admin_pages")
async def admin_pages_process(callback: CallbackQuery, state: FSMContext):
    settings = files.get_settings()
    
    show_table = callback.data.split(" ")[1]
    
    fsm_data = await state.get_data()
    admin_msg = fsm_data[AdminFSM.msg]
    show_data = fsm_data[eval(f"AdminFSM.{show_table}")]
    page = fsm_data[eval(f"AdminFSM.{show_table}_page_n")]
    
    
    kb = keyboards.generate_inline_pages(
        show_table,
        show_data,
        page,
        settings["values"]["admin_page_size"]
    )
    
    await admin_msg.edit_text(
        settings["txt"]["admin_pages"].format(
            show_table.upper(),
            len(show_data),
            page + 1,
            len(show_data) // settings["values"]["admin_page_size"] + 1
        ),
        reply_markup=kb
    )
    
    
@router.callback_query(F.data.split(" ")[0] == "admin_table")
async def admin_table_process(callback: CallbackQuery, state: FSMContext):
    settings = files.get_settings()
    
    table, action, value = callback.data.split(" ")[1:]
    value = int(value)
    
    fsm_data = await state.get_data()
    admin_msg = fsm_data[AdminFSM.msg]
    show_data = fsm_data[eval(f"AdminFSM.{table}")]
    page = fsm_data[eval(f"AdminFSM.{table}_page_n")]
    
    if action == "back":
        await admin_handler(callback.message, state, False)
    elif action == "slide":
        await state.update_data({
            eval(f"AdminFSM.{table}_page_n"): page + value
        })
        
        await admin_pages_process(callback, state)