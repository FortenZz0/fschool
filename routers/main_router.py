from aiogram import types, F, Router, html
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from netschoolapi import NetSchoolAPI

from datetime import datetime, date, timedelta
import sqlite3

from handlers import time_handler as time_h
from handlers import days_handler as days_h
from handlers import diary_handler as diary_h
from handlers import output_handler as out_h
from handlers import marks_handler as marks_h



BUTTONS = {
    "login": "Войти в аккаунт 🔐",
    "diary": "Расписание 🗓",
    "diary_day": "На день",
    "diary_week": "На неделю",
    "marks": "Оценки 🥇",
    "marks_day": "За день",
    "marks_week": "За неделю",
    "marks_cycle": "За учебный период",
    "time": "Время ⏰",
    "school": "О школе 🏫",
    "duty": "Просроченные задания 😎",
    "cycle": "Учебный период",
    "back": "Назад ◀️"
}


router = Router()


db_con = sqlite3.connect(".data.db")
db_cur = db_con.cursor()



class Form(StatesGroup):
    input_login_info = State()

class Using(StatesGroup):
    get_diary = State()
    get_marks = State()
    get_duty = State()
    
class CurrentWeekDiary(StatesGroup):
    week_diary_msg = State()
    week_n = State()



def cut_string(s: str, cut1: str, cut2: str):
    index_1 = s.index(cut1) + len(cut1)
    s = s[index_1:]
    
    index_2 = s.index(cut2)
    return  s[:index_2]


def check_login(tg_us: str) -> bool:
    res = db_cur.execute(f"SELECT tg_us FROM users WHERE tg_us='{tg_us}'")
    
    return bool(res.fetchone())


async def login(tg_us: str,
                url: str,
                lg: str,
                password:str,
                school_name: str,
                cycle_type: str) -> bool:
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
        cycle_type = cycle_type.lower().replace(
            "ч", "quarters"
        ).replace(
            "т",
            "trimesters"
        ).replace(
            "п",
            "half"
        )
        
        values = [
            (tg_us, url, lg, password, school_name, cycle_type)
        ]
        
        db_cur.executemany(f"INSERT INTO users VALUES(?, ?, ?, ?, ?, ?)", values)
        db_con.commit()
        
        await ns.logout()
        return True
        
    return False


def get_current_cycle_type(tg_us: str) -> str:
    cycle_type = db_cur.execute(f"SELECT cycle FROM users WHERE tg_us='{tg_us}'").fetchone()
    
    return cycle_type


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
        

# mode = "base" | "diary" | "marks" | "inline_slider"
def get_keyboard(tg_us: str, mode: str = "base") -> types.ReplyKeyboardMarkup:
    kb = []
    inline_kb = []
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
                types.KeyboardButton(text=BUTTONS["diary_day"]),
                types.KeyboardButton(text=BUTTONS["diary_week"])
            ],
            [
                types.KeyboardButton(text=BUTTONS["back"])
            ]
        ]
        
    elif mode == "inline_slider":
        kb = [
            [
                types.InlineKeyboardButton(
                    text="ЗАГРУЗИТЬ",
                    callback_data='inline_slider_load',
                    
                )  
            ],
            [
                types.InlineKeyboardButton(
                    text="<<<<",
                    callback_data='inline_slider_prev'
                ),
                types.InlineKeyboardButton(
                    text=">>>>",
                    callback_data='inline_slider_next'
                )
            ]
        ]
        
        return types.InlineKeyboardMarkup(inline_keyboard=kb)
    
    elif mode == "marks":
        kb = [
            [
                types.KeyboardButton(text=BUTTONS["marks_day"]),
                types.KeyboardButton(text=BUTTONS["marks_week"])
            ],
            [
                types.KeyboardButton(text=BUTTONS["marks_cycle"])
            ],
            [
                types.KeyboardButton(text=BUTTONS["back"])
            ]
        ]
    
    else:
        kb = [[types.KeyboardButton(text=BUTTONS["back"])]]
    
        
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder=placeholder,
        one_time_keyboard=one_click
    )
        
    return keyboard


def get_inline_keyboard(questions: dict) -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    # Добавляем кнопки вопросов
    for question_id, question_data in questions.items():
        builder.row(
            types.InlineKeyboardButton(
                text=question_data.get('qst'),
                callback_data=f'qst_{question_id}'
            )
        )
    # Настраиваем размер клавиатуры
    builder.adjust(1)
    return builder.as_markup()



@router.message(Command("start"))
async def start_handler(msg: Message):
    keyboard = get_keyboard(msg.from_user.username)
    
    await msg.answer(
"Приветствую! 👋\nFSchool Bot - это универсальный помощник для взаимодействия с электронными дневниками. \
В нём собраны различные полезные функции, к которым все пользователи имеют мгновенный доступ!",
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
  [НАЗВАНИЕ ШКОЛЫ]\n\
  [УЧЕБНЫЙ ПЕРИОД (Ч|Т|П)]\n\n\
Подсказка, где брать эти данные:\n\
- Сайт дневника: ссылка на эл. дневник (https://####.ru)\n\
      Либо воспользуйтесь {html.link('Списком инстансов СГО', 'https://web.archive.org/web/20221204181741/https://sg-o.ru/')}\n\
      (некоторые ссылки устарели)\n\
- Ваш логин: в настройках аккаунта эл. дневника\n\
- Ваш пароль: в настройках аккаунта эл. дневника\n\
- Название школы: в информации о школе в эл. дневнике\n\
- Учебный период: Ч - Четверти, Т - Триместры, П - Полугодия"
    )
    
    await state.set_state(Form.input_login_info)
    


@router.message(Form.input_login_info)
async def login_process(msg: Message, state: FSMContext):
    info = msg.text.split("\n")
    
    # чтп: четверти, триместры, полугодия
    if not info or len(info) < 5 or info[4].lower() not in "чтп":
        await msg.answer("❌ Получены некорректные данные! Убедитесь в правильности ввода и повторите попытку")
        await state.set_state(Form.input_login_info)
        
        return
    
    repl_message = await msg.answer(
        "Данные получены! Проверяю возможность входа в аккаунт..."
    )
    
    tg_us = msg.from_user.username
    url, lg, password, school_name, cycle_type = info
    
    if await login(tg_us, url, lg, password, school_name, cycle_type):
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

@router.message(F.text.lower() == BUTTONS["back"].lower())
async def back_handler(msg: Message, state: FSMContext):
    await msg.answer(
        "Выберите команду",
        reply_markup=get_keyboard(msg.from_user.username)
    )
    
    await state.clear()


@router.message(F.text.lower() == BUTTONS["diary"].lower())
async def diary_handler(msg: Message, state: FSMContext):
    await msg.answer(
        "Какое расписание вывести?",
        reply_markup=get_keyboard(msg.from_user.username, "diary")
    )
    
    await state.set_state(Using.get_diary)
    
    
@router.message(Using.get_diary)
async def diary_process(msg: Message):
    t = "[Расписание] "
    
    if msg.text.lower() == BUTTONS["diary_day"].lower():
        await msg.answer(
            t + out_h.print_unload_day_by_date(date.today()),
            reply_markup=get_keyboard(msg.from_user.username, "inline_slider")
        )

    elif msg.text.lower() == BUTTONS["diary_week"].lower():
        await msg.answer(
            t + out_h.print_unload_week_by_n(0),
            reply_markup=get_keyboard(msg.from_user.username, "inline_slider")
        )
    
    # await state.clear()


@router.callback_query(F.data.in_(["inline_slider_prev", "inline_slider_next"]))
async def inline_slider_move_handler(callback: types.CallbackQuery):
    header = callback.message.text.split("\n\n")[0]
    
    t = cut_string(header, "[", "]")
    
    if "неделя" in header.lower():
        if callback.data == "inline_slider_prev":
            week_start = cut_string(header, "(", ")").split(" - ")[0]
            week_start_date = datetime.fromisoformat(week_start)
            
            new_week_day = week_start_date - timedelta(days=1)
        else:
            week_end = cut_string(header, "(", ")").split(" - ")[1]
            week_end_date = datetime.fromisoformat(week_end)
        
            new_week_day = week_end_date + timedelta(days=1)
        
        await callback.message.edit_text(
            text=f"[{t}] " + out_h.print_unload_week_by_date(new_week_day),
            reply_markup=callback.message.reply_markup
        )
        
    elif "день" in header.lower():
        day = datetime.fromisoformat(header.split(" ")[-1])
        
        if callback.data == "inline_slider_prev":
            new_day = day - timedelta(days=1)
        else:
            new_day = day + timedelta(days=1)
        
        await callback.message.edit_text(
            text=f"[{t}] " + out_h.print_unload_day_by_date(new_day.date()),
            reply_markup=callback.message.reply_markup
        )
        
    elif "учебный период" in header.lower():
        current_cycle_type = get_current_cycle_type(callback.from_user.username)[0]
        
        cycle_name = cut_string(header, ": ", " (")
        cycles = days_h.get_schooldays()[current_cycle_type]
        
        for i, cycle in enumerate(cycles):
            if cycle_name != cycle["name"]:
                continue
                
            if callback.data == "inline_slider_prev":
                new_i = i - 1
            else:
                new_i = i + 1
                
            if new_i >= len(cycles):
                new_i = 0
            elif new_i < 0:
                new_i = len(cycles) - 1
                
            await callback.message.edit_text(
                text=f"[{t}] " + out_h.print_unload_cycle_by_date(
                    current_cycle_type,
                    date.fromisoformat(cycles[new_i]["start"])
                ),
                reply_markup=callback.message.reply_markup
            )
    
    
@router.callback_query(F.data == "inline_slider_load")
async def inline_slider_load_handler(callback: types.CallbackQuery):
    header = callback.message.text.split("\n\n")[0]
    
    t = cut_string(header, "[", "]")
    
    output = "Не удалось подключиться к эл. дневнику!"
    
    ns = await get_NetSchoolAPI(callback.from_user.username)
    
    if ns:
        output = "-- ПУСТО --"
        
        if "неделя" in header.lower() or "учебный период" in header.lower():
            week_start, week_end = cut_string(header, "(", ")").split(" - ")
            
            start_date = date.fromisoformat(week_start)
            end_date = date.fromisoformat(week_end)
        
        elif "день" in header.lower():
            day = datetime.fromisoformat(header.split(" ")[-1]).date()
                
            start_date = day
            end_date = day
        
        if t == "Расписание":
            diary = await diary_h.get_diary(ns, start_date, end_date)
            
            if diary:
                out = out_h.print_diary(diary)
                
                output = out if out else output
                
        elif t == "Оценки":
            diary = await diary_h.get_diary(ns, start_date, end_date)
            
            if diary:
                out = out_h.print_marks_of_diary(diary)
                
                output = out if out else output
            
    
    await callback.message.edit_text(
        text=header + "\n\n" + output,
        reply_markup=get_keyboard(callback.from_user.username, "inline_slider")
    )
    
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
            "❌ Не удалось подключиться к электронному дневнику!",
        )
        return
    
    info = await out_h.print_school_info(ns)
    await msg.answer(info)
    
    await ns.logout()
    
    
@router.message(F.text.lower() == BUTTONS["marks"].lower())
async def marks_handler(msg: Message, state: FSMContext):
    await msg.answer(
        "Оценки за какой период вывести?",
        reply_markup=get_keyboard(msg.from_user.username, "marks")
    )
    
    await state.set_state(Using.get_marks)
    
    
@router.message(Using.get_marks)
async def marks_process(msg: Message):
    t = "[Оценки] "
    
    if msg.text.lower() == BUTTONS["marks_day"].lower():
        await msg.answer(
            t + out_h.print_unload_day_by_date(date.today()),
            reply_markup=get_keyboard(msg.from_user.username, "inline_slider")
        )
    elif msg.text.lower() == BUTTONS["marks_week"].lower():
        await msg.answer(
            t + out_h.print_unload_week_by_n(0),
            reply_markup=get_keyboard(msg.from_user.username, "inline_slider")
        )
    elif msg.text.lower() == BUTTONS["marks_cycle"].lower():
        cycle_type = get_current_cycle_type(msg.from_user.username)[0]
        
        day = date.today()
        
        await msg.answer(
            t + out_h.print_unload_cycle_by_date(cycle_type, day),
            reply_markup=get_keyboard(msg.from_user.username, "inline_slider")
        )
        
        
@router.message(F.text.lower() == BUTTONS["duty"].lower())
async def duty_handler(msg: Message):
    ns = await get_NetSchoolAPI(msg.from_user.username)
    
    if not ns:
        await msg.answer(
            "❌ Не удалось подключиться к электронному дневнику!",
        )
        return
    
    cycle_type = get_current_cycle_type(msg.from_user.username)[0]
    cycles = days_h.get_schooldays()[cycle_type]

    start_date = date.fromisoformat(cycles[0]["start"])
    end_date = date.fromisoformat(cycles[-1]["end"])
    
    diary = await diary_h.get_diary(ns, start_date, end_date)
    
    if not diary:
        await msg.answer(
            "❌ Не удалось получить данные из дневника!",
        )
        await ns.logout()
        return
    
    output = out_h.print_duty_of_diary(diary)
    
    await msg.answer(output)
    await ns.logout()