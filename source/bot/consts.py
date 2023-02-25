from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode
from aiogram.utils.executor import Executor

from source.core.misc import settings

bot = Bot(token=settings.tg_bot_token, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())
executor = Executor(dispatcher=dp, skip_updates=True)