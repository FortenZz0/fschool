from datetime import datetime, date, time
from netschoolapi import NetSchoolAPI
from netschoolapi.schemas import Lesson, Day, Diary
import asyncio
import json



# ПОЛУЧИТЬ ДЕНЬ ПО ДАТЕ
async def get_day(ns: NetSchoolAPI, day_date: date) -> Day:
    today_diary = await ns.diary(start=day_date, end=day_date)
    day = today_diary.schedule[0]
    
    return day


# ПОЛУЧИТЬ ТЕКУЩИЙ ДЕНЬ
async def get_current_day(ns: NetSchoolAPI) -> Day:
    # today = date.today()
    today = date(2024, 5, 20)
    
    day = await get_day(ns, today)
    
    return day


# ПАРСИНГ ./handlers/schooldays.json
def get_schooldays() -> dict:
    with open("handlers/schooldays.json", "r", encoding="utf-8") as f:
        return json.loads(f.read())



# ПОЛУЧИТЬ ДАТЫ НАЧАЛА И КОНЦА ЧЕТВЕРТИ/ТРИМЕСТРА ПО ДАТЕ
# cycle_type = "quarters" | "trimesters"
def get_cycle_by_date(cycle_type: str, target_date: date) -> tuple[str, date, date] | None:
    schooldays = get_schooldays()

    for cycle in schooldays[cycle_type]:
        start = date.fromisoformat(cycle["start"])
        end = date.fromisoformat(cycle["end"])
        
        if start <= target_date <= end:
            return cycle["name"], start, end
        
    return None


# ПОЛУЧИТЬ ДАТЫ НАЧАЛА И КОНЦА ЧЕТВЕРТИ/ТРИМЕСТРА ПО НОМЕРУ
# cycle_type = "quarters" | "trimesters"
def get_cycle_by_n(cycle_type: str, n: int) -> tuple[str, date, date] | None:
    schooldays = get_schooldays()
    
    cycles = schooldays[cycle_type]
    target_cycle = cycles[n]
    
    start = date.fromisoformat(target_cycle["start"])
    end = date.fromisoformat(target_cycle["end"])
    
    return target_cycle["name"], start, end
    

# ПОЛУЧИТЬ ДАТЫ НАЧАЛА И КОНЦА ТЕКУЩЕЙ ЧЕТВЕРТИ/ТРИМЕСТРА
# cycle_type = "quarters" | "trimesters"
def get_current_cycle(cycle_type: str) -> list[Day]:
    # today = date.today()
    today = date(2024, 5, 20)
    
    return get_cycle_by_date(cycle_type, today)
    


# ПОЛУЧИТЬ ДНЕВНИК ЧЕТВЕРТИ/ТРИМЕСТРА ПО ДАТЕ
# cycle_type = "quarters" | "trimesters"
async def get_cycle_diary_by_date(ns: NetSchoolAPI, cycle_type: str, target_date: date) -> Diary:
    _, start, end = get_cycle_by_date(cycle_type, target_date)
    
    diary = await ns.diary(start=start, end=end)
    
    return diary


# ПОЛУЧИТЬ ДНЕВНИК ЧЕТВЕРТИ/ТРИМЕСТРА ПО НОМЕРУ
# cycle_type = "quarters" | "trimesters"
async def get_cycle_diary_by_n(ns: NetSchoolAPI, cycle_type: str, n: int) -> Diary:
    _, start, end = get_cycle_by_n(cycle_type, n)
    
    diary = await ns.diary(start=start, end=end)
    
    return diary


# ПОЛУЧИТЬ ДНЕВНИК ТЕКУЩЕЙ ЧЕТВЕРТИ/ТРИМЕСТРА
# cycle_type = "quarters" | "trimesters"
async def get_cycle_diary_by_n(ns: NetSchoolAPI, cycle_type: str) -> Diary:
    # today = date.today()
    today = date(2024, 5, 20)
    
    _, start, end = get_cycle_by_date(cycle_type, today)
    
    diary = await ns.diary(start=start, end=end)
    
    return diary