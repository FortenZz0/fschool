from aiogram import types, F, Router, html
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from netschoolapi import NetSchoolAPI

from handlers import database, files, keyboards
from handlers.login import *
from handlers.fsm import *

from .settings_router import cycle_translate

import asyncio



router = Router(name=__name__)
ACTIVE = True
db = database.DB()



def new_admin(tg_username: str) -> bool:
    """Записывает нового админа в базу данных

    Args:
        tg_username (str): Тг юз админа
    """
    
    # if not get_user(tg_username):
    #     return False
    
    db.execute(
        "INSERT INTO admins(username, using_username) VALUES(?, ?)",
        (tg_username, tg_username)
    )
    
    db.commit()



# Получение списка юзеров и админов и запись в FSM
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


# Главная страница админки
@router.message(F.text.lower() == files.get_settings()["buttons"]["reply"]["admin"].lower())
async def admin_handler(msg: Message, state: FSMContext, new_msg: bool = True):
    if new_msg:
        admin_data = get_admin(msg.from_user.username)
        
        if not admin_data:
            return
    else:
        admin_data = get_admin(msg.chat.username)
    
    settings = files.get_settings()
    
    data = await load_data(state)
    kb = keyboards.get_inline("admin_main", data)
    
    if new_msg:
        admin_msg = await msg.answer(
            settings["txt"]["admin_main"].format(*admin_data),
            reply_markup=kb
        )
    else:
        admin_msg = msg
        await msg.edit_text(
            settings["txt"]["admin_main"].format(*admin_data),
            reply_markup=kb
        )
    
    await state.update_data({
        AdminFSM.msg: admin_msg,
        AdminFSM.users_page_n: 0,
        AdminFSM.admins_page_n: 0
    })


# Просмотр таблиц через админку
@router.callback_query(F.data.split(" ")[0] == "admin_pages")
async def admin_pages_handler(callback: CallbackQuery, state: FSMContext):
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


# Обработка нажатий кнопок в просмотре таблиц
@router.callback_query(F.data.split(" ")[0] == "admin_table")
async def admin_table_handler(callback: CallbackQuery, state: FSMContext):
    settings = files.get_settings()
    
    table, action, value = callback.data.split(" ")[1:]
    
    fsm_data = await state.get_data()
    admin_msg = fsm_data[AdminFSM.msg]
    show_data = fsm_data[eval(f"AdminFSM.{table}")]
    page = fsm_data[eval(f"AdminFSM.{table}_page_n")]
    
    if action == "back": # Назад
        await admin_handler(callback.message, state, False)
    
    elif action == "slide": # Страница вперёд/назад
        await state.update_data({
            eval(f"AdminFSM.{table}_page_n"): page + int(value)
        })
        
        await admin_pages_handler(callback, state)
    
    elif action == "add": # Добавить запись в таблицу
        kb = keyboards.get_inline("admin_add_back", [table])
        
        await admin_msg.edit_text(
            text=settings["txt"][f"admin_add_{table}"],
            reply_markup=kb
        )
        
        await state.set_state(AdminFSM.new_query)
        await state.update_data({AdminFSM.new_query_table: table})
    
    elif action == "show": # Показать подробности о записи
        data = list(show_data[int(value)])
        
        if table == "admins":
            user_data = get_user(data[0])
            
            if user_data:
                data = list(user_data) + [data[1]]
            else:
                data = [data[0], *["---" for _ in range(5)], data[1]] 
        
        kb = keyboards.get_inline("admin_query_page", [table, data[0]])
        
        if data[5] in list(cycle_translate.keys()):
            data[5] = cycle_translate[data[5]]
        
        await admin_msg.edit_text(
            text=settings["txt"][f"admin_show_{table}"].format(*data),
            reply_markup=kb
        )
    
    elif action == "del": # Удалить запись
        db.execute(f"DELETE FROM {table} WHERE username = ?", (value,))
        db.commit()
        
        await admin_msg.edit_text(
            text=settings["txt"][f"admin_del_{table}"].format(value),
            reply_markup=None
        )
        
        await asyncio.sleep(1)
        
        await admin_handler(admin_msg, state, False)
                    

# Обработка добавления записи в таблицу
@router.message(AdminFSM.new_query)
async def new_query_process(msg: Message, state: FSMContext):
    settings = files.get_settings()
    
    fsm_data = await state.get_data()
    admin_msg = fsm_data[AdminFSM.msg]
    table = fsm_data[AdminFSM.new_query_table]
    
    if table == "users": # Добавление юзера
        data = msg.text.split("\n")
        
        if get_user(data[0]):            
            await admin_msg.edit_text(
                text=settings["txt"]["admin_user_exists_error"],
                reply_markup=keyboards.get_inline("admin_add_back", [table])
            )
            
            return
        
        ns = await ns_login(*data[1:])
        
        if not ns:
            await admin_msg.edit_text(
                text=settings["txt"]["admin_user_login_error"],
                reply_markup=keyboards.get_inline("admin_add_back", [table])
            )
            return
        
        await ns.logout()
        
        new_user(*data)
        
        await admin_msg.edit_text(
            text=settings["txt"]["admin_add_user_success"],
            reply_markup=None
        )
        
        await asyncio.sleep(1)
        
        await admin_handler(admin_msg, state, False)
    
    elif table == "admins": # Добавление админа
        admin_username = msg.text.split("\n")[0]
        
        if get_admin(admin_username):            
            await admin_msg.edit_text(
                text=settings["txt"]["admin_exists_error"],
                reply_markup=keyboards.get_inline("admin_add_back", [table])
            )
            
            return
        
        new_admin(admin_username)
        
        await admin_msg.edit_text(
            text=settings["txt"]["admin_add_admin_success"],
            reply_markup=None
        )
        
        await asyncio.sleep(1)
        
        await admin_handler(admin_msg, state, False)


# Изменение целевого(просматриваемого) аккаунта для админов
@router.callback_query(F.data == "admin_set_target")
async def admin_set_target_handler(callback: CallbackQuery, state: FSMContext):
    settings = files.get_settings()
    
    fsm_data = await state.get_data()
    admin_msg = fsm_data[AdminFSM.msg]
    
    kb = keyboards.get_inline("admin_set_target")
    
    await admin_msg.edit_text(
        text=settings["txt"]["admin_set_target"],
        reply_markup=kb
    )
    await state.set_state(AdminFSM.set_target)


# Возврат целевого(просматриваемого) аккаунта для админов к исходному аккаунту админов
@router.callback_query(F.data.split(" ")[0] == "admin_target")
async def admin_target_handler(callback: CallbackQuery, state: FSMContext):
    action = callback.data.split(" ")[1]
    
    fsm_data = await state.get_data()
    admin_msg = fsm_data[AdminFSM.msg]
    admin_username = admin_msg.chat.username
    
    if action == "set_self":
        db.execute(
            "UPDATE admins SET using_username = ? WHERE username = ?",
            (admin_username, admin_username)
        )
        db.commit()
    
    await state.set_state(AdminFSM.empty)
    await admin_handler(admin_msg, state, False)


# Назначение целевого аккаунта для админа
@router.message(AdminFSM.set_target)
async def admin_target_process(msg: Message, state: FSMContext):
    settings = files.get_settings()
    
    fsm_data = await state.get_data()
    admin_msg = fsm_data[AdminFSM.msg]
    admin_username = admin_msg.chat.username
    
    target_username = msg.text.split("\n")[0]
    user = get_user(target_username)
    
    if user:
        db.execute(
            "UPDATE admins SET using_username = ? WHERE username = ?",
            (target_username, admin_username)
        )
        db.commit()
        
        await state.set_state(AdminFSM.empty)
        await msg.delete()
        await admin_handler(admin_msg, state, False)
    else:
        error = settings["txt"]["admin_set_target_error"]
        
        if admin_msg.html_text != error:
            kb = keyboards.get_inline("admin_set_target")
            
            new_admin_msg = await admin_msg.edit_text(
                text=error,
                reply_markup=kb
            )
            
            await state.update_data({AdminFSM.msg: new_admin_msg})
        await msg.delete()