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
    "Элективный курс \"Методология решения задач по физике\"": "Физика ЭЛЕКТИВ",
    "Алгебра и начала математического анализа": "Алгебра",
    "Основы безопасности жизнедеятельности": "ОБЖ",
    "Иностранный язык (английский).": "Английский",
    "Иностранный язык (немецкий).": "Немецкий",
    "Вероятность и статистика": "Вер. и Стат.",
    "Физическая культура": "Физкультура",
    "Информатика и ИКТ": "Информатика",
    "Русский язык": "Русский"
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
            
        if homework and homework.count("-") < len(homework):
            output += f"\n      - {homework}"
    
    return output
  
  
# ВЫВОД ДНЕВНИКА
def print_diary(diary: Diary) -> str:
    output = []
    
    for i, day in enumerate(diary.schedule):
        output.append(print_day(day, i+1))
        
    return "\n\n".join(output)
