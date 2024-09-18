from datetime import datetime, date, time, timedelta, timezone
from netschoolapi import NetSchoolAPI
from timezonefinder import TimezoneFinder
from netschoolapi.schemas import Lesson
from geopy import geocoders
import asyncio


from handlers import days_handler as dh



geo = geocoders.Yandex("3dd22f85-15b3-4db6-8fbc-04dcb63a878e")

tf = TimezoneFinder()



async def get_now(ns: NetSchoolAPI):
    tz_convert = {
        "Europe/Kaliningrad":  lambda x: x + timedelta(seconds=60*60*2),
        "Europe/Moscow":       lambda x: x + timedelta(seconds=60*60*3),
        "Europe/Samara":       lambda x: x + timedelta(seconds=60*60*4),
        "Asia/Yekaterinburg":  lambda x: x + timedelta(seconds=60*60*5),
        "Asia/Omsk":           lambda x: x + timedelta(seconds=60*60*6),
        "Asia/Krasnoyarsk":    lambda x: x + timedelta(seconds=60*60*7),
        "Asia/Irkutsk":        lambda x: x + timedelta(seconds=60*60*8),
        "Asia/Yakutsk":        lambda x: x + timedelta(seconds=60*60*9),
        "Asia/Vladivostok":    lambda x: x + timedelta(seconds=60*60*10),
        "Asia/Magadan":        lambda x: x + timedelta(seconds=60*60*11),
        "Asia/Kamchatka":      lambda x: x + timedelta(seconds=60*60*12),
    }
    
    info = await ns.school()
    addr = info.address
    
    loc = geo.geocode(addr)
    tz_name = tf.timezone_at(lng=loc.longitude, lat=loc.latitude)
    
    now = datetime.now(timezone.utc)
    
    return tz_convert[tz_name](now)
    


# СКОЛЬКО ВРЕМЕНИ ОСТАЛОСЬ ДО КОНЦА УРОКА/ПЕРЕМЕНЫ
# -1 - уч день ещё не начался
# 0 - сейчас перемена, либо занятия не начались. возвращается время до начала следующего урока
# 1 - сейчас урок. возвращается время до конца текущего урока
# 2 - день кончился, уроков больше не будет. возвращается текущее время
async def subject_time_left(ns: NetSchoolAPI) -> tuple[int, time] | int | None:
    day = await dh.get_current_day(ns)
    
    if not day:
        return None
    
    # now = datetime.now()
    now = await get_now(ns)
    
    for i, lesson in enumerate(day.lessons):
        lesson_start = datetime.combine(now.date(), lesson.start)
        lesson_end = datetime.combine(now.date(), lesson.end)
        current = datetime.combine(now.date(), now.time())
        
        # перемена. время до начала урока
        if lesson_start > current:
            if i == 0:
                return -1
            else:
                return 0, lesson_start - current
        
        # урок. время до начала перемены
        elif lesson_start <= current and lesson_end > current:
            return 1, lesson_end - current
        
        # после уроков. текущее время
        elif lesson_end <= current and i == len(day.lessons) - 1:
            return 2, current.time()
        
        
# СКОЛЬКО ВРЕМЕНИ ОСТАЛОСЬ ДО НАЧАЛА/КОНЦА УЧЕБНОГО ДНЯ
# 0 - до начала
# 1 - до конца
# None - уч день окончен
async def day_time_left(ns: NetSchoolAPI) -> tuple[int, time] | None:
    day = await dh.get_current_day(ns)
    
    if not day:
        return None
    
    # now = datetime.now()
    now = await get_now(ns)
    
    start_day = datetime.combine(now.date(), day.lessons[0].start, timezone.utc)
    end_day = datetime.combine(now.date(), day.lessons[-1].end, timezone.utc)
    
    if now < start_day:
        return 0, start_day - now
    elif start_day > now < end_day:
        return 1, end_day - now
    else:
        return None