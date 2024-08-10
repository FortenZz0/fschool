from datetime import datetime, date, time
from netschoolapi import NetSchoolAPI
from netschoolapi.schemas import Lesson, Day, Diary
import asyncio
import json



# ПОЛУЧИТЬ ДЕНЬ ПО ДАТЕ
async def get_day(ns: NetSchoolAPI, day_date: date) -> Day | None:
    today_diary = await ns.diary(start=day_date, end=day_date)
    
    if not today_diary.schedule:
        return None
    
    day = today_diary.schedule[0]
    
    return day


# ПОЛУЧИТЬ ТЕКУЩИЙ ДЕНЬ
async def get_current_day(ns: NetSchoolAPI) -> Day | None:    
    day = await get_day(ns, date.today())
    
    return day


# ПОЛУЧИТЬ СЛЕДУЮЩИЙ ДЕНЬ
async def get_next_day(ns: NetSchoolAPI) -> Day | None: 
    today = date.today()
    next_day = date(today.year, today.month, today.day + 1)
       
    day = await get_day(ns, next_day)
    
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
    
    if n >= len(cycles):
        return None
    
    target_cycle = cycles[n]
    
    start = date.fromisoformat(target_cycle["start"])
    end = date.fromisoformat(target_cycle["end"])
    
    return target_cycle["name"], start, end
    

# ПОЛУЧИТЬ ДАТЫ НАЧАЛА И КОНЦА ТЕКУЩЕЙ ЧЕТВЕРТИ/ТРИМЕСТРА
# cycle_type = "quarters" | "trimesters"
def get_current_cycle(cycle_type: str) -> list[Day]:    
    return get_cycle_by_date(cycle_type, date.today())


# ПОЛУЧИТЬ ДАТЫ НАЧАЛА И КОНЦА ЧЕТВЕРТИ/ТРИМЕСТРА ПОСЛЕ (ИЛИ ПЕРЕД) ТЕКУЩИМ
# cycle_type = "quarters" | "trimesters"
# add: int -- какой цикл по счёту после (или перед, если add < 0) текущего
def get_add_cycle(cycle_type: str, add: int) -> tuple[str, date, date]:
    today = date.today()
    
    cycles = get_schooldays()[cycle_type]
    
    for i, cycle in enumerate(cycles):
        current_start = date.fromisoformat(cycle["start"])
        
        next_i = i + add
        if next_i >= len(cycles):
            next_i = 0
            
        next_cycle = get_cycle_by_n(cycle_type, next_i)
        next_start = next_cycle[1]
        
        
        if current_start <= today < next_start:
            return next_cycle
        
    return get_cycle_by_n(cycle_type, 0)
    


# ПОЛУЧИТЬ КОЛИЧЕСТВО ДНЕЙ ДО КОНЦА ТЕКУЩЕЙ ЧЕТВЕРТИ/ТРИМЕСТРА/КАНИКУЛ
# 0 - дней до конца каникул
# 1 - дней до конца четверти/триместра
def get_cycle_days_left(cycle_type: str) -> tuple[int, int]:
    t = 1
    cycle = get_current_cycle(cycle_type)
    
    if not cycle:
        cycle = get_add_cycle(cycle_type, 1)
        t = 0
    
    print(cycle)
    
    end = cycle[t+1]
    
    return end - date.today(), t
    
    