import logging
import os
import sys
from typing import Optional, Union, List, Dict
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import asyncio
from aiogram import Bot, Dispatcher, Router
from aiogram import F, types
from aiogram.types import BotCommand, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
import aiogram.utils.markdown as fmt
from aiogram.fsm.state import State, StatesGroup

from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
import argparse

def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_type",
                        help = "Choose API type (default: None)",
                        default=None,
                        choices=['polling','webhook'])
    return parser

WEB_SERVER_HOST = "127.0.0.1"
WEB_SERVER_PORT = 8080
WEBHOOK_PATH = os.environ.get('WEBHOOK_PATH', '')

WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', '')
#BASE_WEBHOOK_URL = 
BASE_WEBHOOK_URL = os.environ.get('BASE_WEBHOOK_URL', '')
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '')

bot = Bot(token=TELEGRAM_TOKEN,default=DefaultBotProperties(parse_mode=ParseMode.HTML))
router = Router()

class Context(StatesGroup):
    selecting_journals = State()
    waiting_for_keywords = State()
    processing_keywords = State()


JOURNALS = [
    "JCP",
    "JQSRT",
]

JOURNALS_CBK = [
    "JCP_pressed",
    "JQSRT_pressed",
]
assert(len(JOURNALS_CBK) == len(JOURNALS))

FINALIZE_JOURNALS_TEXT = "Finalize selection"
FINALIZE_JOURNALS_CBK = "finalize_journal_selection_pressed"

FINALIZE_KEYWORDS_TEXT = "Finalize selection"
FINALIZE_KEYWORDS_CBK = "finalize_keywords_selection_pressed"

LEXICON: Dict[str, str] = {
    "/start": "Dear User,\nThis is a service bot designed to keep track of recently released articles in the subject area you are interested in.\n"
              "Please, select the journal from the list below. More journals will soon be available!",
    FINALIZE_JOURNALS_CBK: "Thank you! Your journal selection has been saved. Please enter the comma separated list of keywords.",
    FINALIZE_KEYWORDS_CBK: "Thank you! The entered keywords have been saved. Stay tuned for notifications!"
}


users_journal_db: Dict[int, List[int]]  = {}
users_keywords_db: Dict[int, List[str]] = {}

def build_keyboard(options: List[str], callback_data: List[str], finalize_button_text: str, finalize_button_cbk: str, *selected_options: str) -> InlineKeyboardMarkup:
    assert len(options) == len(callback_data)

    buttons = []
    for journal, cbk in zip(options, callback_data):
        if journal in selected_options:
            button = InlineKeyboardButton(text=journal + " is added", callback_data=cbk)
        else:
            button = InlineKeyboardButton(text=journal, callback_data=cbk)

        buttons.append(button)

    if finalize_button_text and finalize_button_cbk:
        buttons.append(
            InlineKeyboardButton(text=finalize_button_text, callback_data=finalize_button_cbk)
        )

    return InlineKeyboardMarkup(inline_keyboard=[[button] for button in buttons])

def build_journal_keyboard(*selected_options: str) -> InlineKeyboardMarkup:
    return build_keyboard(JOURNALS, JOURNALS_CBK, FINALIZE_JOURNALS_TEXT, FINALIZE_JOURNALS_CBK, *selected_options)


@router.message(Command("start"))
async def command_start_handler(message: types.Message, state: FSMContext):
    await bot.send_message(message.chat.id, fmt.text(LEXICON['/start']), reply_markup=build_journal_keyboard())
    await state.set_state(Context.selecting_journals)


@router.callback_query(F.data.in_(JOURNALS_CBK))
async def process_journal_select(callback: CallbackQuery):
    if isinstance(callback.message, types.InaccessibleMessage) or callback.message is None:
        logging.info(f"process_journal_select: callback received broken/empty message. Ignoring the selection...")
        return

    user_id = callback.message.chat.id

    if callback.data is not None:
        journal_id = JOURNALS_CBK.index(callback.data)
    else:
        logging.info("process_journal_select: callback content is empty. Ignoring the selection...")
        return

    if user_id not in users_journal_db:
        users_journal_db[user_id] = [journal_id]
        await bot.answer_callback_query(callback.id, text="Journal is selected!")
    elif journal_id in users_journal_db[user_id]:
        users_journal_db[user_id].remove(journal_id)
        await bot.answer_callback_query(callback.id, text="Journal is removed!")
    else:
        users_journal_db[user_id].append(journal_id)
        await bot.answer_callback_query(callback.id, text="Journal is selected!")

    logging.info("User id={} => {}".format(user_id, users_journal_db[user_id]))

    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=build_journal_keyboard(*[JOURNALS[ind] for ind in users_journal_db[user_id]])
    )


@router.callback_query(Context.selecting_journals and F.data == FINALIZE_JOURNALS_CBK)
async def finalize_journal_selection(callback: CallbackQuery, state: FSMContext):
    if isinstance(callback.message, types.InaccessibleMessage) or callback.message is None:
        logging.info(f"finalize_journal_selection: callback received broken/empty message. Ignoring the selection...")
        return

    user_id = callback.message.chat.id

    if user_id not in users_journal_db.keys() or not users_journal_db[user_id]:
        await bot.answer_callback_query(callback.id, text="No options selected!")
        return

    logging.info("User: {} => selected journals: {}".format(user_id, users_journal_db[user_id]))

    await bot.answer_callback_query(callback.id, text="Selection finalized!")
    await bot.send_message(callback.message.chat.id, LEXICON[FINALIZE_JOURNALS_CBK])
    await state.set_state(Context.waiting_for_keywords)


def uniq(seq):
    # https://stackoverflow.com/questions/480214/how-do-i-remove-duplicates-from-a-list-while-preserving-order 
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


@router.message(Context.waiting_for_keywords)
async def process_keywords(message: types.Message, state: FSMContext):
    if message.text is None:
        logging.info("process_keywords: message is empty. Ignoring it...")
        return

    keywords = message.text.split(',')
    keywords = [keyword.strip() for keyword in keywords if keyword.strip()]  # Remove any extra spaces

    if message.from_user is None:
        logging.info("process_keywords: from_user field is empty. Could not get user from the message. Ignoring it...")
        return

    user_id = message.from_user.id
    if user_id not in users_keywords_db:
        users_keywords_db[user_id] = keywords
    else:
        users_keywords_db[user_id].extend(keywords)
        users_keywords_db[user_id] = uniq(users_keywords_db[user_id])

    keywords = users_keywords_db[user_id]
    logging.info("User: {} => selected keywords: {}".format(user_id, keywords))

    await bot.send_message(
        message.from_user.id,
        "Here are the keywords you submitted. Clicking on the corresponding button allows you to remove the unwanted items from the list. You can also type in additional comma-separated keywords, which will be included in the list.",
        reply_markup=build_keyboard(keywords, keywords, FINALIZE_KEYWORDS_TEXT, FINALIZE_KEYWORDS_CBK)
        # NOTE: is this a good idea to use the keywords themselves as callback_data for the buttons?
    )


@router.callback_query(Context.waiting_for_keywords and F.data != FINALIZE_KEYWORDS_CBK)
async def remove_keyword(callback: CallbackQuery):
    if isinstance(callback.message, types.InaccessibleMessage) or callback.message is None:
        logging.info(f"remove_keyword: callback received broken/empty message. Ignoring the selection...")
        return
    
    user_id = callback.message.chat.id

    keyword = callback.data
    await callback.answer()

    assert keyword in users_keywords_db[user_id]
    users_keywords_db[user_id].remove(keyword)
    keywords = users_keywords_db[user_id]

    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=build_keyboard(keywords, keywords, FINALIZE_KEYWORDS_TEXT, FINALIZE_KEYWORDS_CBK)
    )


@router.callback_query(Context.waiting_for_keywords and F.data == FINALIZE_KEYWORDS_CBK)
async def finalize_keywords_selection(callback: CallbackQuery, state: FSMContext):
    if isinstance(callback.message, types.InaccessibleMessage) or callback.message is None:
        logging.info(f"finalize_keywords_selection: callback received broken/empty message. Ignoring the selection...")
        return

    user_id = callback.message.chat.id
    
    logging.info("User: {} => selected keywords: {}".format(user_id, users_keywords_db[user_id]))

    if user_id not in users_keywords_db.keys() or not users_keywords_db[user_id]:
        await bot.answer_callback_query(callback.id, text="Please, submit at least 1 keyword!")
        return

    await bot.answer_callback_query(callback.id, text="Keywords selection finalized!")
    await bot.send_message(callback.message.chat.id, LEXICON[FINALIZE_KEYWORDS_CBK])
    await state.clear()

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


async def main_polling():
    logging.debug("Entered main_polling()")
    dp = Dispatcher()
    dp.include_router(router)
    dp.startup.register(set_main_menu_polling)
    await dp.start_polling(bot)

###async def on_startup(bot: Bot) -> None:
#    # If you have a self-signed SSL certificate, then you will need to send a public
#    # certificate to Telegram
#    await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}", secret_token=WEBHOOK_SECRET)
#
async def on_startup():
    await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}", secret_token=WEBHOOK_SECRET)


def main_webhook():
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
            main_webhook()
            #asyncio.run(main_webhook())
        #main_webhook()
        #web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)
        #print(type(app))
        #print(type())
        elif api_type == 'polling':
            asyncio.run(main_polling())
    except Exception as e:
        print('Some exception occured!',e)
#    dp.include_router(router)
#    dp.startup.register(set_main_menu)
#    dp.run_polling(bot)
