from datetime import datetime, date, time, timedelta, timezone
from netschoolapi import NetSchoolAPI
from timezonefinder import TimezoneFinder
from netschoolapi.schemas import Lesson, Diary
from geopy import geocoders
import asyncio

from handlers import files, calendar, schemas, diary



def get_marks(diary: schemas.MyDiary) -> schemas.MyMarks:
    """Преобразует объект дневника MyDiary в объект MyMarks

    Args:
        diary (MyDiary): Объект дневника

    Returns:
        MyMarks: Объект оценок
    """
    
    return schemas.MyMarks(diary)


async def get_day_marks(ns: NetSchoolAPI,
                        add_days: int = 0,
                        skip_sunday: bool = True) -> schemas.MyMarks | None:
    """Получение оценок за день

    Args:
        ns (NetSchoolAPI): Объект NetSchoolAPI
        add_days (int, optional): Сколько дней нужно добавить к дате дневника. Defaults to 0.
        skip_sunday (bool, optional): Пропускать ли воскресенье. Defaults to True.

    Returns:
        MyMarks | None: Оценки за день
    """
    
    d = await diary.get_day_diary(ns, add_days, skip_sunday)
    
    return get_marks(d)


async def get_week_marks(ns: NetSchoolAPI,
                         add_weeks: int = 0,
                         skip_sunday: bool = True) -> schemas.MyMarks | None:
    """Получение оценок за неделю

    Args:
        ns (NetSchoolAPI): Объект NetSchoolAPI
        add_days (int, optional): Сколько дней нужно добавить к неделе дневника. Defaults to 0.
        skip_sunday (bool, optional): Пропускать ли воскресенье. Defaults to True.

    Returns:
        MyMarks | None: Оценки за неделю
    """
    
    d = await diary.get_week_diary(ns, add_weeks, skip_sunday)
    
    return get_marks(d)


async def get_cycle_marks(ns: NetSchoolAPI,
                          cycle_type: str,
                          add_cycles: int = 0) -> schemas.MyMarks | None:
    """Получение оценок за учебный период

    Args:
        ns (NetSchoolAPI): Объект NetSchoolAPI
        add_days (int, optional): Сколько периодов нужно добавить к текущему периоду. Defaults to 0.
        skip_sunday (bool, optional): Пропускать ли воскресенье. Defaults to True.

    Returns:
        MyMarks | None: Оценки за учебный период
    """
    
    start, end, _ = await calendar.get_cycle(ns, cycle_type, add_cycles)
    
    d = await diary.get_diary(ns, start, end)
    
    return get_marks(d)