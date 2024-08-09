from datetime import datetime, date, time
from netschoolapi import NetSchoolAPI
import asyncio

from handlers import time_handler as time_h
from handlers import days_handler as days_h
from handlers import diary_handler as diary_h



async def main():
    ns = NetSchoolAPI("https://sgo1.edu71.ru")
    
    await ns.login(
        'Верховцев',
        '789964kOl)',
        'МБОУ «ЦО № 34»'
    )
    
    print(await time_h.day_time_left(ns))
    
    await ns.logout()
    
    
if __name__ == '__main__':
    asyncio.run(main())

