from datetime import datetime, date, time
from netschoolapi import NetSchoolAPI
import asyncio

from dotenv import find_dotenv, load_dotenv
from os import getenv

from handlers import time_handler as time_h
from handlers import days_handler as days_h
from handlers import diary_handler as diary_h
from handlers import output_handler as out_h
from handlers import marks_handler as marks_h


denv = find_dotenv()
load_dotenv(denv)


async def main():
    ns = NetSchoolAPI(getenv("MY_URL"))
    
    await ns.login(
        getenv("MY_LOGIN"),
        getenv("MY_PASS"),
        getenv("MY_SCHOOLE_NAME")
    )
    
    print(await out_h.print_school_info(ns))
    
    
    await ns.logout()
    
    
if __name__ == '__main__':
    asyncio.run(main())

