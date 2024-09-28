from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext



# FSM для входа в аккаунт эл.ж.
class LoginFSM(StatesGroup):
    msg = State()
    url = State()
    login = State()
    password = State()
    school = State()
    edit_url = State()
    edit_login = State()
    edit_password = State()
    edit_school = State()
    
    
# FSM для настроек
class SettingsFSM(StatesGroup):
    msg = State()
    username = State()
    cycle = State()