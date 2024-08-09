from datetime import datetime, date, time
from netschoolapi import NetSchoolAPI
from netschoolapi.schemas import Lesson
import asyncio

from handlers import days_handler as dh



# СКОЛЬКО ВРЕМЕНИ ОСТАЛОСЬ ДО КОНЦА УРОКА/ПЕРЕМЕНЫ
# 0 - сейчас перемена, либо занятия не начались. возвращается время до начала следующего урока
# 1 - сейчас урок. возвращается время до конца текущего урока
# 2 - день кончился, уроков больше не будет. возвращается текущее время
async def subject_time_left(ns: NetSchoolAPI) -> tuple[int, time, Lesson | None]:
    day = await dh.get_current_day(ns)
    
    now = datetime.now()
    
    for i, lesson in enumerate(day.lessons):
        lesson_start = datetime.combine(now.date(), lesson.start)
        lesson_end = datetime.combine(now.date(), lesson.end)
        current = datetime.combine(now.date(), now.time())
        
        # перемена. время до начала урока
        if lesson_start > current:
            next_lesson = None
            
            if i < len(day.lessons) - 1:
                next_lesson = day.lessons[i+1]
            
            return 0, lesson_start - current, next_lesson
        
        # урок. время до начала перемены
        elif lesson_start <= current and lesson_end > current:
            return 1, lesson_end - current, lesson
        
        # после уроков. текущее время
        elif lesson_end <= current and i == len(day.lessons) - 1:
            return 2, current.time(), None
        
        
# СКОЛЬКО ВРЕМЕНИ ОСТАЛОСЬ ДО КОНЦА УЧЕБНОГО ДНЯ
async def day_time_left(ns: NetSchoolAPI) -> time | None:
    day = await dh.get_current_day(ns)
    
    if not day:
        return None
    
    now = datetime.now()
    end_day = datetime.combine(now.date(), day.lessons[-1].end)
    
    if now < end_day:
        return end_day - now
    else:
        return time.min
    