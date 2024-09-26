#TODO: adminn access with a filter by chat_id
#TODO: delete keyboard once "finalize" is reached
#TODO: use aiosqlite or some other asynchronous database framework
#TODO: rewrite requests to the journals websites using aiohttp
import logging
import os
import sys
from typing import Optional, Union, List, Dict
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import asyncio
from aiogram import Bot, Dispatcher, Router
from aiogram import F, types
from aiogram.types import BotCommand
from aiogram.filters import Command, CommandStart
from aiogram.handlers import ErrorHandler

from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
import argparse


from handlers import router

def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_type",
                        help = "Choose API type (default: None)",
                        default=None,
                        choices=['polling','webhook'])
    parser.add_argument("--bot",
                        help = "Choose which bot to use",
                        default=None,
                        choices=['release','debug'])

    return parser

WEB_SERVER_HOST = "127.0.0.1"
WEB_SERVER_PORT = 8080
WEBHOOK_PATH = os.environ.get('WEBHOOK_PATH', '')

WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', '')
#BASE_WEBHOOK_URL = 
BASE_WEBHOOK_URL = os.environ.get('BASE_WEBHOOK_URL', '')
TELEGRAM_TOKEN_RELEASE = os.environ.get('TELEGRAM_TOKEN_RELEASE', '')
TELEGRAM_TOKEN_DEBUG = os.environ.get('TELEGRAM_TOKEN_DEBUG', '')
async def set_main_menu_polling(bot: Bot):
    main_menu = [
        BotCommand(command='/help', description='The description of how to use the bot'),
    ]

    #elif api_type == 'polling':
    #    asyncio.run(main_polling())
    await bot.set_my_commands(main_menu)

async def set_main_menu_webhook(bot: Bot):
    main_menu = [
        BotCommand(command='/help', description='The description of how to use the bot'),
    ]

    await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}", secret_token=WEBHOOK_SECRET)
    logging.debug("Webhook was set")
    #elif api_type == 'polling':
    #    asyncio.run(main_polling())
    await bot.set_my_commands(main_menu)


async def main_polling(bot: Bot):
    logging.debug("Entered main_polling()")
    dp = Dispatcher()
    dp.include_router(router)
    dp.startup.register(set_main_menu_polling)
    #INFO: synchronous dp.run_polling() in fact calls asynchronous dp.start_polling()
    await dp.start_polling(bot)


#async def on_startup():
#    await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}", secret_token=WEBHOOK_SECRET)


def main_webhook(bot: Bot):
    logging.debug("Entered main_webhook()")

    dp = Dispatcher()
    dp.include_router(router)
    dp.startup.register(set_main_menu_webhook)
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    )
    app = web.Application()
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)
    #asyncio.run(web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT))


#TODO: Does the main function have to be asynchronous? 
async def depr_main_webhook():
    logging.debug("Entered main_webhook()")

    dp = Dispatcher()
    dp.include_router(router)
    dp.startup.register(set_main_menu_webhook)
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET,
    )
    #NOTE: https://stackoverflow.com/questions/53465862/python-aiohttp-into-existing-event-loop
    app = web.Application()
    #  webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    #setup_application(app, dp, bot=bot)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner,host=WEB_SERVER_HOST,port=WEB_SERVER_PORT)
    await site.start()
    print("===== Running ======")
    await asyncio.sleep(3600)
        #await asyncio.Event().wait()
    #await web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)
    #asyncio.run(web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT))

if __name__ == "__main__":
    parser = build_arg_parser()
    args = parser.parse_args()
    if args.bot == 'debug':
        bot = Bot(token=TELEGRAM_TOKEN_DEBUG,default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    elif args.bot == 'release':
        bot = Bot(token=TELEGRAM_TOKEN_RELEASE,default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    logging.root.handlers = []
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("main.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    api_type = args.api_type
    try:
        if api_type == 'webhook':
            main_webhook(bot)
            #asyncio.run(main_webhook())
        #main_webhook()
        #web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)
        #print(type(app))
        #print(type())
        elif api_type == 'polling':
            asyncio.run(main_polling(bot))
    except Exception as e:
        print('Some exception occured!',e)
#    dp.include_router(router)
#    dp.startup.register(set_main_menu)
#    dp.run_polling(bot)
