from datetime import datetime, date, time
from netschoolapi import NetSchoolAPI
from netschoolapi.schemas import Lesson
import asyncio



# СКОЛЬКО ВРЕМЕНИ ОСТАЛОСЬ ДО КОНЦА УРОКА/ПЕРЕМЕНЫ
# 0 - сейчас перемена, либо занятия не начались. возвращается время до начала следующего урока
# 1 - сейчас урок. возвращается время до конца текущего урока
# 2 - день кончился, уроков больше не будет. возвращается текущее время
async def how_many_time(ns: NetSchoolAPI) -> tuple[int, time, Lesson | None]:
    # today = date.today()
    today = date(2024, 5, 20)
    
    today_diary = await ns.diary(start=today, end=today)
    day = today_diary.schedule[0]
    
    current_time = datetime.now().time()
    
    for i, lesson in enumerate(day.lessons):
        # перемена. время до начала урока
        if lesson.start > current_time:
            a = datetime.combine(today, current_time)
            b = datetime.combine(today, lesson.start)
            
            next_lesson = None
            
            if i < len(day.lessons) - 1:
                next_lesson = day.lessons[i+1]
            
            return 0, b - a, next_lesson
        
        # урок. время до начала перемены
        elif lesson.start <= current_time and lesson.end > current_time:
            a = datetime.combine(today, current_time)
            b = datetime.combine(today, lesson.end)
            
            return 1, b - a, lesson
        
        # после уроков. текущее время
        elif lesson.end <= current_time and i == len(day.lessons) - 1:
            return 2, current_time, None