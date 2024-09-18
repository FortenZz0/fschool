from netschoolapi import NetSchoolAPI
from netschoolapi.schemas import Diary
from io import BytesIO
import asyncio

from handlers.output_handler import translate_subject



async def download_file(ns: NetSchoolAPI, attachment_id: int, file_name: str) -> tuple[BytesIO, str]:
    buffer = BytesIO()
    
    await ns.download_attachment(attachment_id, buffer)
    
    # save_file(file_name, buffer)
    return buffer, file_name


async def get_files_from_diary(ns: NetSchoolAPI, diary: Diary):
    downloaded_files = []
    
    for day in diary.schedule:
        for lesson in day.lessons:
            for ass in lesson.assignments:
                for i, att in enumerate(await ns.attachments(ass.id)):
                    ext = att.name.split(".")[-1]
                    
                    file_name = f"{translate_subject(lesson.subject)} {lesson.day} ({i}).{ext}"
                    
                    file = await download_file(ns, att.id, file_name)
                    downloaded_files.append(file)
    
    return downloaded_files