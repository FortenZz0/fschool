from aiogram.types import InlineKeyboardButton, KeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from typing import Iterable
from handlers import files



def get_inline(kb_type: str, data: Iterable = [], sub_str: str = "") -> InlineKeyboardMarkup:
    btn = files.get_settings()["buttons"]["inline"]
    
    min_data_len = 4
    
    if len(data) < min_data_len:
        data += [0 for _ in range(min_data_len - len(data))]
    
    markups = {
        "edit_login_data": [
            [InlineKeyboardButton(text=btn["edit_url"].format(data[0]), callback_data="edit_url")],      # url
            [InlineKeyboardButton(text=btn["edit_login"].format(data[1]), callback_data="edit_login")],  # login
            [InlineKeyboardButton(text=btn["edit_pass"].format(data[2]), callback_data="edit_pass")],    # password
            [InlineKeyboardButton(text=btn["edit_school"].format(data[3]), callback_data="edit_school")] # school
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
            [InlineKeyboardButton(text=btn["sure_yes"], callback_data=f"sure_{sub_str} yes"),
            InlineKeyboardButton(text=btn["sure_no"], callback_data=f"sure_{sub_str} no")]
        ],
        "admin_main": [
            [InlineKeyboardButton(text=btn["admin_users"].format(data[0]), callback_data="admin_pages users")],  # count of users
            [InlineKeyboardButton(text=btn["admin_admins"].format(data[1]), callback_data="admin_pages admins")], # count of admins
            [InlineKeyboardButton(text=btn["admin_change_target"], callback_data="admin_set_target")]
        ],
        "admin_add_back": [
            [InlineKeyboardButton(text=btn["back"], callback_data=f"admin_table {data[0]} back 0")] # table
        ],
        "admin_query_page": [
            [InlineKeyboardButton(text=btn["del"], callback_data=f"admin_table {data[0]} del {data[1]}"), # table, username
            InlineKeyboardButton(text=btn["back"], callback_data=f"admin_table {data[0]} back 0")] # table
        ],
        "admin_set_target": [
            [InlineKeyboardButton(text=btn["admin_set_self_target"], callback_data=f"admin_target set_self"), # table, username
            InlineKeyboardButton(text=btn["back"], callback_data=f"admin_target back")] # table
        ],
        "slider_cycle": [
            [InlineKeyboardButton(text=btn["load"], callback_data="slider_load")],
            [InlineKeyboardButton(text=btn["prev"], callback_data="slider_move -1"),
            InlineKeyboardButton(text=btn["next"], callback_data="slider_move 1")]
        ],
        "slider": [
            [InlineKeyboardButton(text=btn["load"], callback_data="slider_load")],
            [
                InlineKeyboardButton(text=btn["prev_n"].format("7"), callback_data="slider_move -7"),
                InlineKeyboardButton(text=btn["prev_n"].format("1"), callback_data="slider_move -1"),
                InlineKeyboardButton(text=btn["next_n"].format("1"), callback_data="slider_move 1"),
                InlineKeyboardButton(text=btn["next_n"].format("7"), callback_data="slider_move 7")
            ]
        ],
        "period": [
            [
                InlineKeyboardButton(text=btn["day_period"], callback_data="period day"),
                InlineKeyboardButton(text=btn["week_period"], callback_data="period week")
            ],
            [InlineKeyboardButton(text=btn["cycle_period"], callback_data="period cycle")]
        ],
        
        "period_short": [
            [
                InlineKeyboardButton(text=btn["day_period"], callback_data="period day"),
                InlineKeyboardButton(text=btn["week_period"], callback_data="period week")
            ]
        ]
    }
    
    return InlineKeyboardMarkup(inline_keyboard=markups[kb_type])


def get_reply(kb_type: str, is_admin: bool) -> ReplyKeyboardMarkup:
    btn = files.get_settings()["buttons"]["reply"]
    one_click = kb_type in []
    
    markups = {
        "main": [
            [
                KeyboardButton(text=btn["diary"]),
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


def generate_inline_pages(pages_type: str,
                          data: Iterable = (),
                          page: int = 0,
                          size: int = 1):
    if not data:
        return None
    
    settings = files.get_settings()
    
    page_size = settings["values"]["admin_page_size"]
    
    start = page * page_size
    all_pages = len(data) // page_size
    
    page_data = data[start:start+size]
    
    buttons = []
    
    for i, item in enumerate(page_data):
        buttons.append([
            InlineKeyboardButton(
                text=f"[{start + i + 1}] {item[0]}", # username
                callback_data=f"admin_table {pages_type} show {start + i}"
            )
        ])
    
    
    if all_pages > 0:
        prv = InlineKeyboardButton(
            text=settings["buttons"]["inline"]["prev"],
            callback_data=f"admin_table {pages_type} slide -1"
        )
        nxt = InlineKeyboardButton(
            text=settings["buttons"]["inline"]["next"],
            callback_data=f"admin_table {pages_type} slide 1"
        )
        
        print(start, all_pages * page_size)
        
        if start == 0:
            buttons.append([nxt])
        elif 0 < start < (all_pages) * page_size:
            buttons.append([prv, nxt])
        else:
            buttons.append([prv])
            
    
    buttons.append([
        InlineKeyboardButton(
            text=settings["buttons"]["inline"]["add"],
            callback_data=f"admin_table {pages_type} add 0"
        ),
        InlineKeyboardButton(
            text=settings["buttons"]["inline"]["back"],
            callback_data=f"admin_table {pages_type} back 0"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)
    