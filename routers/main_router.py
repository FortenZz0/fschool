from aiogram import Router
from aiogram.types import Message




router = Router(name=__name__)


@router.message()
async def message_handler(msg: Message):
    await msg.answer('Hello from my router!')