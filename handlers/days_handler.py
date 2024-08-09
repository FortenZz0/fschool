from datetime import datetime, date, time
from netschoolapi import NetSchoolAPI
from netschoolapi.schemas import Lesson, Day
import asyncio


async def get_day(ns: NetSchoolAPI, day_date: date) -> Day:
    today_diary = await ns.diary(start=day_date, end=day_date)
    day = today_diary.schedule[0]
    
    return day


async def get_current_day(ns: NetSchoolAPI) -> Day:
    # today = date.today()
    today = date(2024, 5, 20)
    
    day = get_current_day(ns, today)
    
    return day