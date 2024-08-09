from datetime import datetime, date, time
from netschoolapi import NetSchoolAPI
import asyncio

from handlers import time_handler as time_h
from handlers import days_handler as days_h
from handlers import diary_handler as diary_h
from handlers import output_handler as out_h
from handlers import marks_handler as marks_h



async def main():
    ns = NetSchoolAPI("https://sgo1.edu71.ru")
    
    await ns.login(
        'Верховцев',
        '789964kOl)',
        'МБОУ «ЦО № 34»'
    )
    
    diary = await diary_h.get_diary(ns, date(2024, 5, 29), date(2024, 5, 30))
        
    # print(out_h.print_diary(diary))
    print(out_h.print_duty_of_diary(diary))
    
    
    await ns.logout()
    
    
if __name__ == '__main__':
    asyncio.run(main())

