
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
# from aiogram.contrib.fsm_storage.files import MemoryStorage
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from settings import TOKEN

storage = MemoryStorage()

# bot = Bot(token=os.getenv('TOKEN'))
bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=storage)





