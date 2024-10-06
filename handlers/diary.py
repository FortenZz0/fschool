from datetime import datetime, date, time, timedelta, timezone
from netschoolapi import NetSchoolAPI
from timezonefinder import TimezoneFinder
from netschoolapi.schemas import Lesson, Diary
from geopy import geocoders
import asyncio

from handlers import files, calendar, schemas



async def get_diary(ns: NetSchoolAPI,
                    start: date,
                    end: date) -> schemas.MyDiary | None:
    """Получение дневника за определённый период

    Args:
        ns (NetSchoolAPI): Объект NetSchoolAPI
        start (date): Начало периода
        end (date): Конец периода

    Returns:
        MyDiary | None: Дневник за период
    """
    
    diary = await ns.diary(start, end)
    
    return schemas.MyDiary(diary)


async def get_day_diary(ns: NetSchoolAPI,
                        add_days: int = 0,
                        skip_sunday: bool = True) -> schemas.MyDiary | None:
    """Получение дневника на день

    Args:
        ns (NetSchoolAPI): Объект NetSchoolAPI
        add_days (int, optional): Сколько дней нужно добавить к дате дневника. Defaults to 0.
        skip_sunday (bool, optional): Пропускать ли воскресенье. Defaults to True.

    Returns:
        MyDiary | None: Дневник на день
    """
    
    now = await calendar.get_day(ns, add_days, skip_sunday)
    
    diary = await get_diary(ns, now, now)
    
    return diary


async def get_week_diary(ns: NetSchoolAPI,
                         add_weeks: int = 0,
                         skip_sunday: bool = True) -> schemas.MyDiary | None:
    """Получение дневника на неделю

    Args:
        ns (NetSchoolAPI): Объект NetSchoolAPI
        add_days (int, optional): Сколько дней нужно добавить к неделе дневника. Defaults to 0.
        skip_sunday (bool, optional): Пропускать ли воскресенье. Defaults to True.

    Returns:
        MyDiary | None: Дневник на день
    """
    
    start, end = await calendar.get_week(ns, add_weeks, skip_sunday)
    
    diary = await get_diary(ns, start, end)
    
    return diary
