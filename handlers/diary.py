from datetime import datetime, date, time, timedelta, timezone
from netschoolapi import NetSchoolAPI
from timezonefinder import TimezoneFinder
from netschoolapi.schemas import Lesson, Diary
from geopy import geocoders
import asyncio

from handlers import files, calendar, schemas



async def get_diary(ns: NetSchoolAPI,
                    start: date,
                    end: date,
                    period_name: str) -> schemas.MyDiary:
    """Получение дневника за определённый период

    Args:
        ns (NetSchoolAPI): Объект NetSchoolAPI
        start (date): Начало периода
        end (date): Конец периода
        period_name (str): Название периода

    Returns:
        MyDiary | None: Дневник за период
    """
    
    diary = await ns.diary(start, end)
    
    return schemas.MyDiary(diary, period_name)


async def get_day_diary(ns: NetSchoolAPI,
                        add_days: int = 0) -> schemas.MyDiary | None:
    """Получение дневника на день

    Args:
        ns (NetSchoolAPI): Объект NetSchoolAPI
        add_days (int, optional): Сколько дней нужно добавить к дате дневника. Defaults to 0.

    Returns:
        MyDiary | None: Дневник на день
    """
    
    now, _, _ = await calendar.get_day(ns, add_days)
    
    diary = await get_diary(ns, now, now)
    
    return diary


async def get_week_diary(ns: NetSchoolAPI,
                         add_weeks: int = 0) -> schemas.MyDiary | None:
    """Получение дневника на неделю

    Args:
        ns (NetSchoolAPI): Объект NetSchoolAPI
        add_days (int, optional): Сколько дней нужно добавить к неделе дневника. Defaults to 0.

    Returns:
        MyDiary | None: Дневник на день
    """
    
    start, end, _ = await calendar.get_week(ns, add_weeks)
    
    diary = await get_diary(ns, start, end)
    
    return diary
