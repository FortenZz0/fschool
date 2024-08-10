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
    "diary_today": "На сегодня",
    "diary_next_day": "На завтра",
    "diary_week": "На неделю",
    "marks": "Оценки 🥇",
    "time": "Время ⏰",
    "school": "О школе 🏫",
    "duty": "Просроченные задания 😎",
    "cycle": "Учебный период",
    "back": "Назад ◀️"
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
        

# mode = "base" | "diary" | "marks"
def get_keyboard(tg_us: str, mode: str = "base") -> types.ReplyKeyboardMarkup:
    kb = []
    placeholder = "Выберите команду"
    one_click = False
    
    if mode == "base":
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
            
            placeholder = "Вход в аккаунт"
            one_click = True
    elif mode == "diary":
        kb = [
            [
                types.KeyboardButton(text=BUTTONS["diary_today"]),
                types.KeyboardButton(text=BUTTONS["diary_next_day"])
            ],
            [
                types.KeyboardButton(text=BUTTONS["diary_week"])
            ],
            [
                types.KeyboardButton(text=BUTTONS["back"])
            ]
        ]
    elif mode == "marks":
        ...
    else:
        kb = [[types.KeyboardButton(text=BUTTONS["back"])]]
    
        
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



# -- Команды --

@router.message(F.text.lower() == BUTTONS["diary"].lower())
async def diary_handler(msg: Message, state: FSMContext):
    await msg.answer(
        "Какое расписание вывести?",
        reply_markup=get_keyboard(msg.from_user.username, "diary")
    )
    
    await state.set_state(Using.get_diary)
    
    
@router.message(Using.get_diary)
async def diary_process(msg: Message, state: FSMContext):
    ns = await get_NetSchoolAPI(msg.from_user.username)
    
    if not ns:
        await msg.answer(
            "❌ Не удалось подключиться к электронному дневнику!",
            reply_markup=get_keyboard(msg.from_user.username)
        )
        return
    
    diary = None
    
    if msg.text.lower() == BUTTONS["diary_today"].lower():
        today = await days_h.get_current_day(ns)
        
        if not today:
            await msg.answer(
                "❌ Сегодня уроков не было!",
                reply_markup=get_keyboard(msg.from_user.username)
            )
            return
        
        diary = await diary_h.get_diary(ns, today.day, today.day)
        
    elif msg.text.lower() == BUTTONS["diary_next_day"].lower():
        next_day = await days_h.get_next_day(ns)
        
        if not next_day:
            await msg.answer(
                "❌ Завтра уроков не будет!",
                reply_markup=get_keyboard(msg.from_user.username)
            )
            return
        
        diary = await diary_h.get_diary(ns, next_day.day, next_day.day)
        
    elif msg.text.lower() == BUTTONS["diary_week"].lower():
        diary = await diary_h.get_diary(ns, None, None)
        
    if not diary:
        await msg.answer(
            "❌ Не удалось получить расписание!",
            reply_markup=get_keyboard(msg.from_user.username)
        )
        return
    
    output = out_h.print_diary(diary)
    
    if not output:
        await msg.answer(
            "❌ Расписание отсутствует!",
            reply_markup=get_keyboard(msg.from_user.username)
        )
        return
    
    await msg.answer(
        output,
        reply_markup=get_keyboard(msg.from_user.username)
    )
    
    await state.clear()
        
    await ns.logout()
        

@router.message(F.text.lower() == BUTTONS["time"].lower())
async def time_handler(msg: Message):
    ns = await get_NetSchoolAPI(msg.from_user.username)
    
    if not ns:
        await msg.answer(
            "❌ Не удалось подключиться к электронному дневнику!"
        )
        return
    
    subj_time_left = await out_h.print_subject_time_left(ns)
    day_time_left = await out_h.print_day_time_left(ns)
    
    await msg.answer(subj_time_left)
    await msg.answer(day_time_left)
    
    await ns.logout()
    


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
    
    ns.logout()