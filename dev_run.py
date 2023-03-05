import logging

from aiogram.types import BotCommand

from source.bot.consts import executor, dp, bot
from source.core.setup_logging import setup_logging
from source.bot.handlers.user import register_users_handlers

logger = logging.getLogger(__name__)


def register_all_filters(dp):
    ...


def register_all_handlers(dp):
    register_users_handlers(dp)


async def on_startup(*args, **kwargs):
    logger.info('on_startup')
    await bot.set_my_commands([BotCommand('start', 'Начать')])
    await bot.set_my_commands([BotCommand('tg_id', 'Получить мой tg_id')])
    await bot.set_my_commands([BotCommand('notes_by_myself', 'Мои заметки')])
    await bot.set_my_commands([BotCommand('notes_watching', 'Заметки которые могу смотреть')])
    await bot.set_my_commands([BotCommand('new_note', 'Новая заметка')])


async def on_shutdown(*args, **kwargs):
    logger.info('on_shutdown')


def start_bot():
    setup_logging()

    executor.on_startup(on_startup)
    executor.on_shutdown(on_shutdown)

    register_all_filters(dp)
    register_all_handlers(dp)

    # start
    executor.start_polling(reset_webhook=True, fast=True)


if __name__ == '__main__':
    try:
        start_bot()
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
