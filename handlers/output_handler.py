from datetime import datetime, date, time, timedelta
from netschoolapi import NetSchoolAPI
from netschoolapi.schemas import Diary, Day, Lesson
import asyncio

from handlers import time_handler as time_h
from handlers import days_handler as days_h
from handlers import diary_handler as diary_h
from handlers import marks_handler as marks_h

from aiogram import html


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
    "Основы безопасности и защиты Родины": "ОБЗР",
    "Иностранный язык (немецкий).": "Немецкий",
    "Вероятность и статистика": "Вер. и Стат.",
    "Индивидуальный проект": "Инд. проект",
    "Физическая культура": "Физкультура",
    "Информатика и ИКТ": "Информатика",
    "Русский язык": "Русский"
}


# ЗАМЕНА УРОКА НА БОЛЕЕ КОРОТКУЮ ВЕРСИЮ НАПИСАНИЯ
def translate_subject(subj: str) -> str:
    if subj in list(SUBJECT_TRANSLATE.keys()):
        return SUBJECT_TRANSLATE[subj]
    
    return subj


# ВЫВОД ДНЕВНИКА НА ОДИН ДЕНЬ
def print_day_diary(day: Day, n: int | None = None) -> str:
    output = ""
    
    # -- Номер дня --
    if n != None:
        output += f"{n}. "
    
    # -- День недели --
    weekday = WEEKDAYS[day.day.weekday()]
    output += weekday
    
    output = html.bold(output)
    
    # -- Дата и продолжительность дня --
    day_start = day.lessons[0].start.isoformat()[:-3]
    day_end = day.lessons[-1].end.isoformat()[:-3]
    
    output += html.italic(f" ({day.day.isoformat()} {day_start}-{day_end})")
    
    # -- Уроки --
    for lesson in day.lessons:
        les_start = lesson.start.isoformat()[:-3]
        les_end = lesson.end.isoformat()[:-3]
        
        subj = lesson.subject
        if subj in list(SUBJECT_TRANSLATE.keys()):
            subj = SUBJECT_TRANSLATE[subj]
        
        output += f"\n   {lesson.number}) {subj} " + html.italic(f"({les_start}-{les_end})")
        
        ass = lesson.assignments
        if not ass:
            continue
        
        homework = ""
        marks = []
        
        for a in ass:
            if a.type == "Домашнее задание":
                homework = a.content
                
            if a.mark:
                marks.append(html.bold(str(a.mark)))
                                
        if marks:
            output += f" - [{', '.join(marks)}]"
            
        if homework and homework.count("-") < len(homework):
            output += f"\n      - {homework}"
    
    return output
  
  
# ВЫВОД ДНЕВНИКА
def print_diary(diary: Diary) -> str:
    if not diary:
        return ""
    
    output = []
    
    diary.schedule.sort(key=lambda x: x.day)
    
    for i, day in enumerate(diary.schedule):
        output.append(print_day_diary(day, i+1))
        
    return "\n\n".join(output)


# ВЫВОД ОЦЕНОК В ДНЕВНИКЕ
def print_marks_of_diary(diary: Diary) -> str:
    output = []
    
    marks = marks_h.get_marks_of_diary(diary)
    
    for k, v in marks.items():
        output.append(f"* ({len(v)}) {k}: {v}  --  {sum(v) / len(v):.2}")
    
    return "\n".join(output)


# ВЫВОД ПРОСРОЧЕННЫХ ЗАДАНИЙ В ДНЕВНИКЕ
def print_duty_of_diary(diary: Diary) -> str:
    output = ["Ваши просроченные задания:"]
    
    n = 1
    for day in diary.schedule:
        for lesson in day.lessons:
            for ass in lesson.assignments:
                
                if not ass.is_duty:
                    continue
                
                subj = translate_subject(lesson.subject)
                
                output.append(f"\n{n}. {subj} ({ass.type})")
                output.append(f"   - Задание: {ass.content}")
                output.append(f"   - Получено: {lesson.day}")
                output.append(f"   - Выполнить до: {ass.deadline}")
                
                n += 1
                
    if len(output) == 1:
        output.append("-- ОТСУТСТВУЮТ --")
                
    return "\n".join(output).strip()


# ВЫВОД ВРЕМЕНИ ДО КОНЦА УРОКА/ПЕРЕМЕНЫ
async def print_subject_time_left(ns: NetSchoolAPI) -> str:
    time_left = await time_h.subject_time_left(ns)
    
    if not time_left:
        return "Сегодня выходной или каникулы"
    
    match time_left[0]:
        case 0:
            return f"Минут до НАЧАЛА урока: {time_left[1].seconds // 60}"
        case 1:
            return f"Минут до КОНЦА урока: {time_left[1].seconds // 60}"
        case 2:
            return f"Учебный день окончен"
        
    return "НЕИЗВЕСТНАЯ ОШИБКА"


# ВЫВОД ВРЕМЕНИ ДО КОНЦА УЧЕБНОГО ДНЯ
async def print_day_time_left(ns: NetSchoolAPI) -> str:
    time_left = await time_h.day_time_left(ns)
    
    if time_left == None:
        return "Учебный день окончен"
    else:
        hours = time_left.seconds // 3600
        minutes = (time_left.seconds - hours * 3600) // 60
        seconds = time_left.seconds % 60
        
        return f"До конца учебного дня осталось:\n-  часов: {hours}\n-  минут: {minutes}\n-  секунд: {seconds}"
    
    
# ВЫВОД ИНФОРМАЦИИ О ШКОЛЕ
async def print_school_info(ns: NetSchoolAPI) -> str:
    info = await ns.school()
    
    output = [
        "Краткая информация о Вашей школе:",
        f" * Название: {info.name}",
        f" * Краткое описание: {info.about}",
        f" * Юр. адрес: {info.address}",
        f" * Email: {info.email}",
        f" * Сайт школы: {info.site}",
        f" * Контактный телефон: {info.phone}",
        f" * Директор: {info.director}",
        f" * Зам. по АХЧ: {info.AHC}",
        f" * Зам. по ИТ: {info.IT}",
        f" * Зам. по УВР: {info.UVR}"
    ]
    
    return "\n".join(output).strip()


# ВЫВОД НЕЗАГРУЖЕННОЙ НЕДЕЛИ
def print_unload_week_by_n(week_n: int):
    week_start, week_end, week_n = days_h.get_week_by_n(week_n)
    
    return f"Неделя {week_n} - {html.italic(f'({week_start} - {week_end})')}"


# ВЫВОД НЕЗАГРУЖЕННОЙ НЕДЕЛИ
def print_unload_week_by_date(day: date):
    week_start, week_end, week_n = days_h.get_week_by_date(day)
    
    return f"Неделя {week_n} - {html.italic(f'({week_start} - {week_end})')}"


def print_unload_day_by_date(day: date):
    return f"День {day.isoformat()}"


def print_unload_cycle_by_date(cycle_type: str, day: date):
    cycle = days_h.get_cycle_by_date(cycle_type, day)
    
    return f"Учебный период: {cycle[0]} {html.italic(f'({cycle[1]} - {cycle[2]})')}"