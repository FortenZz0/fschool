from aiogram import types, F, Router, html
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from datetime import datetime, date, time
from netschoolapi import NetSchoolAPI

from handlers import time_handler as time_h
from handlers import days_handler as days_h
from handlers import diary_handler as diary_h
from handlers import output_handler as out_h
from handlers import marks_handler as marks_h



router = Router()




class Form(StatesGroup):
    input_login_info = State()



def check_login(tg_us: str) -> bool:
    return False


async def login(tg_us: str, url: str, lg: str, password: str, school_name: str) -> bool:
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
        
        
        await ns.logout()
        return True
        
    return False
        

def get_keyboard(tg_us: str) -> tuple[types.ReplyKeyboardMarkup, str, bool]:
    kb = []
    placeholder = "Выберите команду"
    one_click = False
    
    if check_login(tg_us):
        kb = [
            [
                types.KeyboardButton(text="Кнопка 1"),
                types.KeyboardButton(text="Кнопка 2")
            ]
        ]
    else:
        kb = [[
                types.KeyboardButton(text="Войти в аккаунт 🔐"),
        ]]
        
        placeholder = "Необходимо войти в аккаунт"
        one_click = True
        
    return kb, placeholder, one_click



@router.message(Command("start"))
async def start_handler(msg: Message):
    kb, placeholder, one_click = get_keyboard(msg.from_user.username)
    
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder=placeholder,
        one_time_keyboard=one_click
    )
    
    await msg.answer("Hello world!", reply_markup=keyboard)



@router.message(F.text.lower() == "войти в аккаунт 🔐")
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
async def login_handler(msg: Message, state: FSMContext):
    info = msg.text.split("\n")
    
    if not info or len(info) < 4:
        await msg.answer("❌ Получены некорректные данные! Убедитесь в правильности ввода и повторите попытку")
        await state.set_state(Form.input_login_info)
        
        return
    
    repl_message = await msg.answer(
        "Данные получены! Проверяю возможность входа в аккаунт..."
    )
    
    if await login(msg.from_user.username, *info):
        await repl_message.edit_text("✅ Данные корректны, вы добавлены в базу данных!")
    else:
        await repl_message.edit_text("❌ Не удаётся войти в аккаунт! Проверьте корректность данных и повторите попытку")
        return
    
    await state.clear()