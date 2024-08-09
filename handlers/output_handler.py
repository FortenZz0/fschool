from datetime import datetime, date, time
from netschoolapi import NetSchoolAPI
from netschoolapi.schemas import Diary, Day, Lesson
import asyncio

from handlers import time_handler as time_h
from handlers import days_handler as days_h
from handlers import diary_handler as diary_h



WEEKDAYS = [
    "Понедельник",
    "Вторник",
    "Среда",
    "Четверг",
    "Пятница",
    "Суббота",
    "Воскресенье"
]

SUBJECT_TRANSLATE = {
    "Алгебра и начала математического анализа": "Алгебра",
    "Физическая культура": "Физкультура"
}


# ВЫВОД ОДНОГО ДНЯ
def print_day(day: Day, n: int | None = None) -> str:
    output = ""
    
    # -- Номер дня --
    if n != None:
        output += f"{n}. "
    
    # -- День недели --
    weekday = WEEKDAYS[day.day.isoweekday() - 1]
    output += weekday
    
    # -- Дата и продолжительность дня --
    day_start = day.lessons[0].start.isoformat()[:-3]
    day_end = day.lessons[-1].end.isoformat()[:-3]
    
    output += f" ({day.day.isoformat()} {day_start}-{day_end})"
    
    # -- Уроки --
    for lesson in day.lessons:
        les_start = lesson.start.isoformat()[:-3]
        les_end = lesson.start.isoformat()[:-3]
        
        subj = lesson.subject
        if subj in list(SUBJECT_TRANSLATE.keys()):
            subj = SUBJECT_TRANSLATE[subj]
        
        output += f"\n   {lesson.number}) {subj} ({les_start}-{les_end})"
        
        ass = lesson.assignments
        if not ass:
            continue
        
        homework = ""
        marks = []
        
        for a in ass:
            if a.type == "Домашнее задание":
                homework = a.content
                
            if a.mark:
                marks.append(str(a.mark))
                                
        if marks:
            output += f" - [{', '.join(marks)}]"
            
        if homework:
            output += f":\n      - {homework}"
    
        
    return output
    
    