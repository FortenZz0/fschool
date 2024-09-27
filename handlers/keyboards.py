from aiogram.types import InlineKeyboardButton, KeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

from typing import Iterable



def get_inline(kb_type: str, data: Iterable | None = None) -> InlineKeyboardMarkup:
    markups = {
        "edit_login_data": [
            [InlineKeyboardButton(text=f"✏️ Ссылка: {data[0]}", callback_data="edit_url")],
            [InlineKeyboardButton(text=f"✏️ Логин: {data[1]}", callback_data="edit_login")],
            [InlineKeyboardButton(text=f"✏️ Пароль: {data[2]}", callback_data="edit_pass")],
            [InlineKeyboardButton(text=f"✏️ Назв шк: {data[3]}", callback_data="edit_school")]
        ]
    }
    
    return InlineKeyboardMarkup(inline_keyboard=markups[kb_type])


def get_reply(kb_type: str, is_admin: bool) -> ReplyKeyboardMarkup:
    markups = {
        "main": [
            [
                KeyboardButton(text="Расписание 🗓"),
                KeyboardButton(text="Оценки 🥇")
            ],
            [
                KeyboardButton(text="Время ⏰"),
                KeyboardButton(text="О школе 🏫")
            ],
            [
                KeyboardButton(text="Просроч. задания 😎"),
                KeyboardButton(text="Объявления ⚡️")
            ]
        ]
    }
    
    m = markups[kb_type]
    
    if is_admin and kb_type in ["main"]:
        m.insert(0, [
            KeyboardButton(text="🥷 Админ-панель 🥷")
        ])
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=m,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    return keyboard