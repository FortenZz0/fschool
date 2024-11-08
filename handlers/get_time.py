from datetime import datetime, timedelta, time, tzinfo
from tabnanny import check
from typing import Any

from netschoolapi import NetSchoolAPI

from .calendar import get_now
from .schemas import MyDay, MyDiary
from .files import get_settings
from .diary import get_diary
from .database import DB


db = DB()


def _get_dhms_from_timedelta(td: timedelta) -> tuple[int, int, int]:
    d = td.days
    h = td.seconds // 3600
    m = (td.seconds - h * 3600) // 60
    s = td.seconds - h * 3600 - m * 60
    
    return d, h, m, s

def _get_format_dhms(td: timedelta) -> str:
    time_format = get_settings()["txt"]["time_format"]
    
    dhms = _get_dhms_from_timedelta(td)
    
    res = []
    chars = "dhms"
    
    for i, item in enumerate(dhms):
        if item:
            res.append(time_format.format(item, chars[i]))
    
    return " ".join(res)


def get_delta(t1: time, t2: time) -> timedelta:
    dt1 = datetime(1, 1, 1, t1.hour, t1.minute, t1.second)
    dt2 = datetime(1, 1, 1, t2.hour, t2.minute, t2.second)
    
    return dt1 - dt2


def _get_day_border(day: MyDay) -> tuple[None, None] | tuple[time, time]:
    if not day.lessons:
        return None
    
    start = day.lessons[0].start
    end = day.lessons[-1].end
    
    return start, end


def _is_study_time(now: datetime, day: MyDay) -> None | bool:
    b = _get_day_border(day)
    
    if not b:
        return None
    
    return b[0] <= now.time() <= b[1]


def _day_is_over(now: datetime, day: MyDay) -> None | bool:
    b = _get_day_border(day)
    
    if not b:
        return None
    
    return now.time() > b[1]


def _get_inday_time_left(now: datetime, day: MyDay) -> str | None:
    txt = get_settings()["txt"]
    
    for i, les in enumerate(day.lessons):
        if day.lessons[i-1].end <= now.time() <= les.start: # сейчас перемена
            d = get_delta(les.start, now.time())
            subj = "перемена"
            next_subj = les.subject
            t = "перемены"
            break

        elif les.start <= now.time() <= les.end: # сейчас урок
            d = get_delta(les.end, now.time())
            subj = les.subject
            next_subj = day.lessons[i+1].subject if i != len(day.lessons) - 1 else "домой"
            t = "урока"
            break
    else:
        return None
    
    res = [txt["now_subj"].format(subj)] # сейчас
    res.append(txt["subj_time_left"].format(t, _get_format_dhms(d))) # до конца урока/перемены
    res.append(txt["next_lesson"].format(next_subj)) # след урок
    res.append(txt["day_time_left"].format("конца", _get_format_dhms(get_delta(day.lessons[-1].end, now.time())))) # до конца уроков
    
    return "\n".join(res)


def _get_outday_time_left(now: datetime, day: MyDay) -> str:
    txt = get_settings()["txt"]
    
    time_delta = get_delta(now.time(), day.lessons[0].start)
    days_delta = day.date - now.date()
    
    delta = timedelta(days=days_delta.days, seconds=time_delta.seconds)
    
    res = [txt["now_subj"].format("уроков нет")]
    res.append(txt["day_time_left"].format("начала", _get_format_dhms(delta)))
    res.append(txt["next_lesson"].format(day.lessons[0].subject))
    
    return "\n".join(res)


async def generate_time_str(ns: NetSchoolAPI) -> str:
    now = await get_now(ns)
    # now = datetime(2024, 11, 8, 9, 14, 5)
    
    db.execute("SELECT * FROM users WHERE login=? AND password=? AND school=?", ns._login_data)
    user = db.fetchone()
    period_name = user[-1]
    
    diary2 = await get_diary(ns, now.date(), now.date() + timedelta(days=100), period_name)
    
    today, next_day = diary2.days[:2]
    
    if _is_study_time(now, today):
        return _get_inday_time_left(now, today)
        
    else:
        check_day = today
        
        if _day_is_over(now, today):
            check_day = next_day
            
        return _get_outday_time_left(now, check_day)