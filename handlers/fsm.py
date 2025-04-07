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
    

# FSM для админки
class AdminFSM(StatesGroup):
    msg = State()
    users = State()
    admins = State()
    users_page_n = State()
    admins_page_n = State()
    current_table = State()
    new_query = State()
    new_query_table = State()
    set_target = State()
    empty = State()
    
    
    
# FSM для слайдера
class SliderFSM(StatesGroup):
    msg = State() # bot msg
    title = State() # str
    obj = State() # MyDiary / MyMarks / ...
    obj_func = State() # Callable
    period_func = State() # Callable
    period_n = State() # int
    period_title = State() # str
    txt_template = State() # str
    ns = State() # NetSchoolApi,
    wait_period = State() # wait period msg
    cache = State() # {period_n: str(obj)}


class GotonsFSM(StatesGroup):
    bot_msg = State() # bot msg
    user_msg = State() # user msg