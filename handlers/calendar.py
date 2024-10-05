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



async def get_today(ns: NetSchoolAPI,
                    skip_sunday: bool = True) -> date:
    """Получение даты с учётом часового пояса юзера

    Args:
        ns (NetSchoolAPI): объект NSAPI
        skip_sunday (bool, optional): Переход на следующий день в воскресенье. Defaults to True.

    Returns:
        date: Дата с учётом часового пояса юзера
    """
    
    now = await get_now(ns)
    
    if skip_sunday and now.weekday() == 6:
        now += timedelta(days=1)
        
    return now.date()


