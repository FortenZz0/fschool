from datetime import datetime, date, time
from netschoolapi import NetSchoolAPI
import asyncio

from handlers import time_handler



async def main():
    ns = NetSchoolAPI("https://sgo1.edu71.ru")
    
    await ns.login(
        'Верховцев',
        '789964kOl)',
        'МБОУ «ЦО № 34»'
    )
    
    print(await time_handler.how_many_time_left(ns))
    
    await ns.logout()
    
    
if __name__ == '__main__':
    asyncio.run(main())

