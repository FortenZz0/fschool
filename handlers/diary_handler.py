from datetime import datetime, date, time
from netschoolapi import NetSchoolAPI
from netschoolapi.schemas import Lesson, Day, Diary
import asyncio

from handlers import days_handler as dh



# ПОЛУЧИТЬ ДНЕВНИК ЧЕТВЕРТИ/ТРИМЕСТРА ПО ДАТЕ
# cycle_type = "quarters" | "trimesters"
async def get_cycle_diary_by_date(ns: NetSchoolAPI, cycle_type: str, target_date: date) -> Diary:
    cycle = dh.get_cycle_by_date(cycle_type, target_date)
    
    if not cycle:
        return None
    
    _, start, end = cycle
    
    diary = await ns.diary(start=start, end=end)
    
    return diary


# ПОЛУЧИТЬ ДНЕВНИК ЧЕТВЕРТИ/ТРИМЕСТРА ПО НОМЕРУ
# cycle_type = "quarters" | "trimesters"
async def get_cycle_diary_by_n(ns: NetSchoolAPI, cycle_type: str, n: int) -> Diary:
    cycle = dh.get_cycle_by_n(cycle_type, n)
    
    if not cycle:
        return None
    
    _, start, end = cycle
    
    diary = await ns.diary(start=start, end=end)
    
    return diary


# ПОЛУЧИТЬ ДНЕВНИК ТЕКУЩЕЙ ЧЕТВЕРТИ/ТРИМЕСТРА
# cycle_type = "quarters" | "trimesters"
async def get_current_cycle_diary(ns: NetSchoolAPI, cycle_type: str) -> Diary | None:
    cycle = dh.get_cycle_by_date(cycle_type, dh.TODAY)
    
    if not cycle:
        return None
    
    _, start, end = cycle
    
    diary = await ns.diary(start=start, end=end)
    
    return diary


# ПОЛУЧИТЬ ДНЕВНИК ПО НАЧАЛЬНОМУ И КОНЕЧНОМУ ДНЮ
async def get_diary(ns: NetSchoolAPI, start: date, end: date) -> Diary | None:
    diary = await ns.diary(start=start, end=end)
    
    return diary