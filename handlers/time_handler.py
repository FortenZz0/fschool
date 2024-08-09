from datetime import datetime, date, time
from netschoolapi import NetSchoolAPI
from netschoolapi.schemas import Lesson
import asyncio

import days_handler



# СКОЛЬКО ВРЕМЕНИ ОСТАЛОСЬ ДО КОНЦА УРОКА/ПЕРЕМЕНЫ
# 0 - сейчас перемена, либо занятия не начались. возвращается время до начала следующего урока
# 1 - сейчас урок. возвращается время до конца текущего урока
# 2 - день кончился, уроков больше не будет. возвращается текущее время
async def how_many_time_left(ns: NetSchoolAPI) -> tuple[int, time, Lesson | None]:
    day = days_handler.get_current_day(ns)
    
    current_time = datetime.now().time()
    
    for i, lesson in enumerate(day.lessons):
        lesson_start = datetime.combine(day.date, lesson.start)
        lesson_end = datetime.combine(day.date, lesson.end)
        current = datetime.combine(day.date, current_time)
        
        # перемена. время до начала урока
        if lesson_start > current:
            next_lesson = None
            
            if i < len(day.lessons) - 1:
                next_lesson = day.lessons[i+1]
            
            return 0, lesson_start - current, next_lesson
        
        # урок. время до начала перемены
        elif lesson.start <= current and lesson_end > current:
            return 1, lesson_end - current, lesson
        
        # после уроков. текущее время
        elif lesson.end <= current and i == len(day.lessons) - 1:
            return 2, current.time(), None