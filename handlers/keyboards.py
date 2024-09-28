from aiogram.types import InlineKeyboardButton, KeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from typing import Iterable
from handlers import files







def get_inline(kb_type: str, data: Iterable = [0, 0, 0, 0], prefix: str = "") -> InlineKeyboardMarkup:
    btn = files.get_settings()["buttons"]["inline"]
    
    markups = {
        "edit_login_data": [
            [InlineKeyboardButton(text=btn["edit_url"].format(data[0]), callback_data="edit_url")],
            [InlineKeyboardButton(text=btn["edit_login"].format(data[1]), callback_data="edit_login")],
            [InlineKeyboardButton(text=btn["edit_pass"].format(data[2]), callback_data="edit_pass")],
            [InlineKeyboardButton(text=btn["edit_school"].format(data[3]), callback_data="edit_school")]
        ],
        "settings_main": [
            [InlineKeyboardButton(text=btn["edit_cycle"], callback_data="edit_cycle")],
            [InlineKeyboardButton(text=btn["account_exit"], callback_data="account_exit")]
        ],
        "edit_cycle": [
            [InlineKeyboardButton(text=btn["cycle_quarters"], callback_data="change_cycle quarters")],
            [InlineKeyboardButton(text=btn["cycle_trimesters"], callback_data="change_cycle trimesters")],
            [InlineKeyboardButton(text=btn["cycle_half"], callback_data="change_cycle half")],
            [InlineKeyboardButton(text=btn["back"], callback_data="settings_back")]
        ],
        "sure": [
            [InlineKeyboardButton(text=btn["sure_yes"], callback_data=f"sure_{prefix} yes"),
            InlineKeyboardButton(text=btn["sure_no"], callback_data=f"sure_{prefix} no")]
        ]
    }
    
    return InlineKeyboardMarkup(inline_keyboard=markups[kb_type])


def get_reply(kb_type: str, is_admin: bool) -> ReplyKeyboardMarkup:
    btn = files.get_settings()["buttons"]["reply"]
    one_click = kb_type in []
    
    markups = {
        "main": [
            [
                KeyboardButton(text=btn["schedule"]),
                KeyboardButton(text=btn["marks"])
            ],
            [
                KeyboardButton(text=btn["time"]),
                KeyboardButton(text=btn["school"])
            ],
            [
                KeyboardButton(text=btn["duty"]),
                KeyboardButton(text=btn["ads"])
            ],
            [
                KeyboardButton(text=btn["settings"])
            ]
        ]
    }
    
    m = markups[kb_type]
    
    if is_admin and kb_type in ["main"]:
        m[-1].append(KeyboardButton(text=btn["admin"]))
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=m,
        resize_keyboard=True,
        one_time_keyboard=one_click
    )
    
    return keyboard