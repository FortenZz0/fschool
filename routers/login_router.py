from aiogram import types, F, Router, html
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from netschoolapi import NetSchoolAPI

from handlers import database, files, keyboards
from handlers.fsm import *

import asyncio



router = Router(name=__name__)
db = database.DB()


trans_table = {
    ord("\n"): " ",
    ord("\t"): " ",
    ord("\b"): " "
}


# --- SELF METHODS ---

# Добавляет / в конце ссылки при необходимости
format_url = lambda x: x if x[-1] == "/" else x + "/"


def new_user(tg_username: str,
             url: str,
             login: str,
             password: str,
             school: str):
    """Записывает нового юзера в базу данных

    Args:
        tg_username (str): Тг юз пользователя
        url (str): Ссылка на электронный журнал
        login (str): Логин юзера
        password (str): Пароль юзера
        school (str): Название школы
    """
    
    db.execute(
        "INSERT INTO users(username, url, login, password, school, cycle) VALUES(?, ?, ?, ?, ?, 'quarters')",
        (tg_username,
         url,
         login,
         password,
         school)
    )
    
    db.commit()


def get_user(username: str) -> tuple:
    """Возвращает запись юзера из базы данных

    Args:
        username (str): Тг юзернейм (@*)

    Returns:
        tuple: Запись юзера в бд
    """
    
    db.execute("SELECT * FROM users WHERE username = ?", (username,))
    return db.fetchone()
    
    
def get_admin(username: str) -> tuple:
    """Возвращает запись админа из базы данных

    Args:
        username (str): Тг юзернейм (@*)

    Returns:
        tuple: Запись админа в бд
    """
    
    db.execute("SELECT * FROM admins WHERE username = ?", (username,))
    return db.fetchone()
    

async def ns_login(url: str | None = None,
             login: str | None = None,
             password: str | None = None,
             school: str | None = None,
             tg_username: str | None = None) -> NetSchoolAPI | None:
    """Выполняет вход в электронный журнал. Если указан tg_username, то вход будет произведён с использованием базы данных

    Args:
        url (str | None, optional): Ссылка на электронный журнал. Defaults to None
        login (str | None, optional): Логин юзера. Defaults to None
        password (str | None, optional): Пароль юзера. Defaults to None
        school (str | None, optional): Название школы. Defaults to None
        tg_username (str | None, optional): Тг юз пользователя. Defaults to None

    Returns:
        NetSchoolAPI: Объект NetSchoolAPI
    """
    
    data = [url, login, password, school]
    
    if tg_username:
        data = get_user(tg_username)[1:-1]
        
    ns = NetSchoolAPI(data[0])
    
    if ns:
        try:
            await ns.login(*data[1:])
            
            return ns
        except:
            return None
    else:
        return None



# --- ROUTER MSG HANDLERS ---

# Начало входа. FSM url
@router.message(Command("start"))
async def start_login_handler(msg: Message, state: FSMContext, sleep: bool = True, check_user: bool = True):
    if check_user:
        if get_user(msg.from_user.username):
            return
    
    settings = files.get_settings()
    
    if sleep:
        await asyncio.sleep(0.5)
    
    login_msg = await msg.answer(settings["txt"]["start_login"])

    await state.set_data({LoginFSM.msg: login_msg})
    await state.set_state(LoginFSM.url)
    

# Получение ссылки на эж. FSM url -> login
@router.message(LoginFSM.url)
async def get_url_process(msg: Message, state: FSMContext):
    settings = files.get_settings()
    
    data = await state.get_data()
    login_msg = data[LoginFSM.msg]
    
    url = format_url(msg.text.translate(trans_table))
    
    if url in settings["instances"]:
        await login_msg.edit_text(settings["txt"]["login_valid_url"])

        await state.update_data({LoginFSM.url: url})
        await state.set_state(LoginFSM.login)
    else:
        if login_msg.text != settings["txt"]["login_invalid_url"]:
            await login_msg.edit_text(settings["txt"]["login_invalid_url"])
        
        await state.set_data({LoginFSM.msg: login_msg})
        
    await msg.delete()


# Получение логина. FSM login -> password
@router.message(LoginFSM.login)
async def get_login_process(msg: Message, state: FSMContext):
    settings = files.get_settings()
    
    data = await state.get_data()
    login_msg = data[LoginFSM.msg]
    
    await login_msg.edit_text(settings["txt"]["login_get_login"])

    await state.update_data({LoginFSM.login: msg.text.translate(trans_table)})
    await state.set_state(LoginFSM.password)
    
    await msg.delete()


# Получение пароля. FSM password -> school
@router.message(LoginFSM.password)
async def get_password_process(msg: Message, state: FSMContext):
    settings = files.get_settings()
    
    data = await state.get_data()
    login_msg = data[LoginFSM.msg]
    
    await login_msg.edit_text(settings["txt"]["login_get_pass"])

    await state.update_data({LoginFSM.password: msg.text.translate(trans_table)})
    await state.set_state(LoginFSM.school)
    
    await msg.delete()


# Получение названия школы. FSM school -> LOGIN
@router.message(LoginFSM.school)
async def get_school_process(msg: Message, state: FSMContext):
    settings = files.get_settings()
    
    data = await state.get_data()
    login_msg = data[LoginFSM.msg]
    
    await state.update_data({LoginFSM.school: msg.text.translate(trans_table)})
    
    await login_msg.edit_text(settings["txt"]["login_get_school"])
    await msg.delete()
    
    await asyncio.sleep(0.6)
    await try_login(state, msg.from_user.username)
    
    
        

# Попытка войти в эж
async def try_login(state: FSMContext, username: str):
    settings = files.get_settings()
    
    data = await state.get_data()
    login_msg = data[LoginFSM.msg]
    url = data[LoginFSM.url]
    login = data[LoginFSM.login]
    password = data[LoginFSM.password]
    school = data[LoginFSM.school]
    
    await login_msg.edit_text(settings["txt"]["login_try"])
    
    ns = await ns_login(url, login, password, school)
    
    if ns:
        new_user(
            username,
            url, login,
            password, school
        )
        
        await login_msg.answer(
            settings["txt"]["login_success"],
            reply_markup=keyboards.get_reply(
                "main",
                bool(get_admin(username))
            )
        )
        
        await login_msg.delete()
        
        await state.clear()
    else:
        await login_msg.edit_text(
            settings["txt"]["login_error"],
            reply_markup=keyboards.get_inline(
                "edit_login_data",
                (url, login, password, school)
            )
        )
    
    

# Начало изменения ссылки
@router.callback_query(F.data == "edit_url")
async def edit_url_handler(callback: CallbackQuery, state: FSMContext):
    settings = files.get_settings()
    
    data = await state.get_data()
    login_msg = data[LoginFSM.msg]
    
    await login_msg.edit_text(settings["txt"]["login_edit_url"])
    
    await state.set_state(LoginFSM.edit_url)
    
    
# Изменение ссылки
@router.message(LoginFSM.edit_url)
async def edit_url_process(msg: Message, state: FSMContext):
    settings = files.get_settings()
    
    data = await state.get_data()
    login_msg = data[LoginFSM.msg]
    
    url = format_url(msg.text.translate(trans_table))
    await msg.delete()
    
    if url in settings["instances"]:
        await state.update_data({LoginFSM.url: url})
        
        await try_login(state, msg.from_user.username)
    else:
        if login_msg.text != settings["txt"]["login_invalid_url"]:
            await login_msg.edit_text(settings["txt"]["login_invalid_url"])
            
            
# Начало изменения логина
@router.callback_query(F.data == "edit_login")
async def edit_login_handler(callback: CallbackQuery, state: FSMContext):
    settings = files.get_settings()
    
    data = await state.get_data()
    login_msg = data[LoginFSM.msg]
    
    await login_msg.edit_text(settings["txt"]["login_edit_login"])
    
    await state.set_state(LoginFSM.edit_login)
    
    
# Изменение логина
@router.message(LoginFSM.edit_login)
async def edit_login_process(msg: Message, state: FSMContext):
    await state.update_data({LoginFSM.login: msg.text.translate(trans_table)})
    
    await msg.delete()
    await try_login(state, msg.from_user.username)
    
    
# Начало изменения пароля
@router.callback_query(F.data == "edit_pass")
async def edit_password_handler(callback: CallbackQuery, state: FSMContext):
    settings = files.get_settings()
    
    data = await state.get_data()
    login_msg = data[LoginFSM.msg]
    
    await login_msg.edit_text(settings["txt"]["login_edit_pass"])
    
    await state.set_state(LoginFSM.edit_password)
    
    
# Изменение пароля
@router.message(LoginFSM.edit_password)
async def edit_password_process(msg: Message, state: FSMContext):
    await state.update_data({LoginFSM.password: msg.text.translate(trans_table)})
    
    await msg.delete()
    await try_login(state, msg.from_user.username)
    
    
# Начало изменения названия школы
@router.callback_query(F.data == "edit_school")
async def edit_school_handler(callback: CallbackQuery, state: FSMContext):
    settings = files.get_settings()
    
    data = await state.get_data()
    login_msg = data[LoginFSM.msg]
    
    await login_msg.edit_text(settings["txt"]["login_edit_school"])
    
    await state.set_state(LoginFSM.edit_school)
    
    
# Изменение названия школы
@router.message(LoginFSM.edit_school)
async def edit_school_process(msg: Message, state: FSMContext):
    await state.update_data({LoginFSM.school: msg.text.translate(trans_table)})
    
    await msg.delete()
    await try_login(state, msg.from_user.username)