import environ

from django.core.management import BaseCommand

from aiogram import Dispatcher, Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage


from bot.handlers import router

env = environ.Env()
TOKEN = env('BOT_TOKEN')

bot = Bot(token=TOKEN)

dp = Dispatcher(storage=MemoryStorage())

dp.include_router(router)
bot_session = AiohttpSession()

async def on_shutdown():
    await bot_session.close()

class Command(BaseCommand):
    def handle(self, *args, **options):
        #dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        dp.run_polling(bot)
