from datetime import datetime, date, time, timedelta, timezone
from netschoolapi import NetSchoolAPI
from timezonefinder import TimezoneFinder
from netschoolapi.schemas import Lesson
from geopy import geocoders
import asyncio

from handlers import files



geo = geocoders.Yandex("3dd22f85-15b3-4db6-8fbc-04dcb63a878e")
tf = TimezoneFinder()

tz_convert = {
    "Europe/Kaliningrad":  lambda x: x + timedelta(seconds=60*60*2),  # UTC+2
    "Europe/Moscow":       lambda x: x + timedelta(seconds=60*60*3),  # UTC+3
    "Europe/Samara":       lambda x: x + timedelta(seconds=60*60*4),  # UTC+4
    "Asia/Yekaterinburg":  lambda x: x + timedelta(seconds=60*60*5),  # UTC+5
    "Asia/Omsk":           lambda x: x + timedelta(seconds=60*60*6),  # UTC+6
    "Asia/Krasnoyarsk":    lambda x: x + timedelta(seconds=60*60*7),  # UTC+7
    "Asia/Irkutsk":        lambda x: x + timedelta(seconds=60*60*8),  # UTC+8
    "Asia/Yakutsk":        lambda x: x + timedelta(seconds=60*60*9),  # UTC+9
    "Asia/Vladivostok":    lambda x: x + timedelta(seconds=60*60*10), # UTC+10
    "Asia/Magadan":        lambda x: x + timedelta(seconds=60*60*11), # UTC+11
    "Asia/Kamchatka":      lambda x: x + timedelta(seconds=60*60*12), # UTC+12
}



async def get_now(ns: NetSchoolAPI) -> datetime:    
    """Получение текущего времени с учётом часового пояса юзера

    Args:
        ns (NetSchoolAPI): Объект NSAPI

    Returns:
        _datetime_: datetime + time zone
    """
    
    info = await ns.school()
    addr = info.address
    
    loc = geo.geocode(addr)
    tz_name = tf.timezone_at(lng=loc.longitude, lat=loc.latitude)
    
    now = datetime.now(timezone.utc)
    
    return tz_convert[tz_name](now)



async def get_day(ns: NetSchoolAPI,
                  add_days: int = 0) -> tuple[date, str]:
    """Получение даты с учётом часового пояса юзера

    Args:
        ns (NetSchoolAPI): объект NSAPI
        add_days (int, optional): Сколько дней нужно добавить к текущей дате. Defaults to 0.
        skip_sunday (bool, optional): Переход на следующий день в воскресенье. Defaults to True.

    Returns:
        date: Дата с учётом часового пояса юзера
    """
    
    week_days = [
        "Понедельник",
        "Вторник",
        "Среда",
        "Четверг",
        "Пятница",
        "Суббота",
        "Воскресенье"
    ]
    
    now = await get_now(ns)
    new_now = now + timedelta(days=add_days)
    
    # if skip_sunday and new_now.weekday() == 6:
    #     add_delta = timedelta(days=1)
        
    #     new_now += add_delta

    #     y_new_now = new_now.timetuple().tm_yday
    #     y_now = now.timetuple().tm_yday
        
    #     delta = abs(y_new_now - y_now)
        
    #     for d in range(1, delta + 1):
    #         delta_date = now + add_delta * (d if y_new_now >= y_now else -d)
            
    #         if delta_date.weekday() == 6:
    #             new_now += timedelta(days=1)
    
    return new_now.date(), week_days[new_now.weekday()]


async def get_week(ns: NetSchoolAPI,
                   add_weeks: int = 0) -> tuple[date, date, int]:
    """Получение текущей недели

    Args:
        ns (NetSchoolAPI): объект NSAPI
        add_weeks (int, optional): Сколько недель нужно добавить к текущей дате. Defaults to 0.
        skip_sunday (bool, optional): Переход на следующий день в воскресенье. Defaults to True.

    Returns:
        tuple[date, date]: Дата начала недели (понедельник) и дата конца недели (суббота)
    """
    
    today = await get_day(ns)
    
    days_to_week_start = today.weekday()
    days_to_week_end = 6 - today.weekday() - 1
    
    week_start = today - timedelta(days=days_to_week_start - add_weeks * 7)
    week_end = today + timedelta(days=days_to_week_end + add_weeks * 7)
    
    week_n = (week_start.isocalendar().week - 35) % 52
    
    return week_start, week_end, week_n


async def get_cycle(ns: NetSchoolAPI,
                    cycle_type: str,
                    add_cycles: int = 0) -> tuple[date, date, str]:
    """Получение текущего учебного периода

    Args:
        ns (NetSchoolAPI): объект NSAPI
        cycle_type (str): Тип учебного периода ["quarters" | "trimesters" | "half"]
        add_cycles (int, optional): Сколько периодов нужно добавить к текущему периоду. Defaults to 0.

    Returns:
        tuple[date, date, str]: Дата начала, дата конца, название
    """
    
    cycles = files.get_settings()["schooldays"][cycle_type]
    
    today = await get_day(ns, skip_sunday=False)
    current_cycle = 0
    
    for i, cycle in enumerate(cycles):
        start = date.fromisoformat(cycle["start"])
        end = date.fromisoformat(cycle["end"])
        
        if today < start: # Каникулы в учебном году
            # Проверка на летние каникулы до начала учебного года
            # Если сейчас летние каникулы, выдаём 1 четверть, иначе прошлую четверть
            if i != 0:
                current_cycle -= 1
            break
        elif start <= today <= end: # Учебный период
            current_cycle = i
            break
        else: # Если мы не попали ни в уч. п., ни в каникулы, прибавляем
            current_cycle += 1
    else: # Летние каникулы после учебного года
        current_cycle -= 1
    
    current_cycle = (current_cycle + add_cycles) % len(cycles)
    
    cycle = cycles[current_cycle]
    cycle_start = date.fromisoformat(cycle["start"])
    cycle_end = date.fromisoformat(cycle["end"])
    cycle_name = cycle["name"]
    
    return cycle_start, cycle_end, cycle_name
    
    