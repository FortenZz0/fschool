from aiogram import types, F, Router, html
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from netschoolapi import NetSchoolAPI

import sqlite3

from handlers import time_handler as time_h
from handlers import days_handler as days_h
from handlers import diary_handler as diary_h
from handlers import output_handler as out_h
from handlers import marks_handler as marks_h



BUTTONS = {
    "login": "Войти в аккаунт 🔐",
    "diary": "Расписание 🗓",
    "marks": "Оценки 🥇",
    "time": "Время до... ⏰",
    "school": "О школе 🏫",
    "duty": "Просроченные задания 😎"
}


router = Router()


db_con = sqlite3.connect("data.db")
db_cur = db_con.cursor()



class Form(StatesGroup):
    input_login_info = State()



class Using(StatesGroup):
    get_diary = State()
    get_marks = State()
    get_time = State()
    get_duty = State()



def check_login(tg_us: str) -> bool:
    res = db_cur.execute(f"SELECT tg_us FROM users WHERE tg_us='{tg_us}'")
    
    return bool(res.fetchone())


async def login(tg_us: str, url: str, lg: str, password: str, school_name: str) -> bool:
    if check_login(tg_us):
        return True
    
    success = False
    
    ns = NetSchoolAPI(url)
    
    if not ns:
        return False
    
    try:
        await ns.login(
            lg,
            password,
            school_name
        )
        
        success = True
        
    except:
        return False
    
    if success and ns:
        values = [
            (tg_us, url, lg, password, school_name)
        ]
        
        db_cur.executemany(f"INSERT INTO users VALUES(?, ?, ?, ?, ?)", values)
        db_con.commit()
        
        await ns.logout()
        return True
        
    return False


async def get_NetSchoolAPI(tg_us: str) -> NetSchoolAPI | None:
    data = db_cur.execute(f"SELECT url, login, pass, school_name FROM users WHERE tg_us='{tg_us}'").fetchone()
    
    if not data:
        return None
    
    ns = NetSchoolAPI(data[0])
    
    try:
        await ns.login(*data[1:])
        
        return ns
    except:
        return None
        

def get_keyboard(tg_us: str) -> types.ReplyKeyboardMarkup:
    kb = []
    placeholder = "Выберите команду"
    one_click = False
    
    if check_login(tg_us):
        kb = [
            [
                types.KeyboardButton(text=BUTTONS["diary"]),
                types.KeyboardButton(text=BUTTONS["marks"])
            ],
            [
                types.KeyboardButton(text=BUTTONS["time"]),
                types.KeyboardButton(text=BUTTONS["school"])
            ],
            [
                types.KeyboardButton(text=BUTTONS["duty"])
            ]
        ]
    else:
        kb = [[
                types.KeyboardButton(text=BUTTONS["login"]),
        ]]
        
        placeholder = "Необходимо войти в аккаунт"
        one_click = True
        
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder=placeholder,
        one_time_keyboard=one_click
    )
        
    return keyboard



@router.message(Command("start"))
async def start_handler(msg: Message):
    keyboard = get_keyboard(msg.from_user.username)
    
    await msg.answer(
"Приветствую! 👋\nFSchool - это универсальный помощник для взаимодействия с электронными дневниками. \
В нём собраны различные полезные функции, к которым все пользователи имеют мгновенный доступ!\n\n\
Из плюсов:\n\
  ✅ Не нужно входить в аккаунт КАЖДЫЕ 5 МИНУТ (что не скажешь о большинстве эл. дневников)\n\
  ✅ БЫСТРЫЙ и БЕСПЛАТНЫЙ доступ ко всему функционалу сразу после входа в аккаунт\n\
  ✅ Широкий список полезных функций, которых нет ни в одном электронном дневнике",
        reply_markup=keyboard
    )
    
    if not check_login(msg.from_user.username):
        await msg.answer(f"Для входа в аккаунт своего электронного дневника используй кнопку \"{BUTTONS['login']}")



@router.message(F.text.lower() == BUTTONS["login"].lower())
async def login_handler(msg: Message, state: FSMContext):
    await msg.answer(
f"Отправьте одним сообщением следующие данные для входа в аккаунт сетевого дневника (без скобок):\n\
  [САЙТ ДНЕВНИКА]\n\
  [ВАШ ЛОГИН]\n\
  [ВАШ ПАРОЛЬ]\n\
  [НАЗВАНИЕ ШКОЛЫ]\n\n\
Подсказка, где брать эти данные:\n\
- Сайт дневника: ссылка на эл. дневник (https://####.ru)\n\
      Либо воспользуйтесь {html.link('Списком инстансов СГО', 'https://web.archive.org/web/20221204181741/https://sg-o.ru/')}\n\
      (некоторые ссылки устарели)\n\
- Ваш логин: в настройках аккаунта эл. дневника\n\
- Ваш пароль: в настройках аккаунта эл. дневника\n\
- Название школы: в информации о школе в эл. дневнике"
    )
    
    await state.set_state(Form.input_login_info)
    


@router.message(Form.input_login_info)
async def login_process(msg: Message, state: FSMContext):
    info = msg.text.split("\n")
    
    if not info or len(info) < 4:
        await msg.answer("❌ Получены некорректные данные! Убедитесь в правильности ввода и повторите попытку")
        await state.set_state(Form.input_login_info)
        
        return
    
    repl_message = await msg.answer(
        "Данные получены! Проверяю возможность входа в аккаунт..."
    )
    
    tg_us = msg.from_user.username
    
    if await login(tg_us, *info):
        await repl_message.delete()
        
        await msg.answer(
            "✅ Данные корректны, вы добавлены в базу данных!",
            reply_markup=get_keyboard(tg_us)
        )
    else:
        await repl_message.edit_text("❌ Не удаётся войти в аккаунт! Проверьте корректность данных и повторите попытку")
        return
    
    await state.clear()
    
    
    


@router.message(F.text.lower() == BUTTONS["school"].lower())
async def school_handler(msg: Message):
    ns = await get_NetSchoolAPI(msg.from_user.username)
    
    if not ns:
        await msg.answer(
            "❌ Не удалось подключиться к электронному дневнику!"
        )
        
        return
    
    info = await out_h.print_school_info(ns)
    await msg.answer(info)