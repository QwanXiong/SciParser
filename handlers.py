
import asyncio
from aiogram import F, types
from aiogram.types import BotCommand, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
import aiogram.utils.markdown as fmt
from aiogram.fsm.state import State, StatesGroup
from aiogram.handlers import ErrorHandler
from typing import Optional, Union, List, Dict
import logging
from aiogram import Router

from loggers import bot_err_logger

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


@router.message(Command("invoke_error"))
async def command_invoke_error_handler(message: types.Message, state: FSMContext):
    await message.answer("Error raised")
    raise RuntimeError("This is error")

@router.message(Command("start"))
async def command_start_handler(message: types.Message, state: FSMContext):
    #await bot.send_message(message.chat.id, fmt.text(LEXICON['/start']), reply_markup=build_journal_keyboard())
    await message.answer(fmt.text(LEXICON['/start']), reply_markup=build_journal_keyboard())
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

        #await bot.answer_callback_query(callback.id, text="Journal is selected!")
        await callback.answer(text="Journal is selected!")
    elif journal_id in users_journal_db[user_id]:
        users_journal_db[user_id].remove(journal_id)
        await callback.answer(text="Journal is removed!")
    else:
        users_journal_db[user_id].append(journal_id)
        await callback.answer(text="Journal is selected!")

    logging.info("User id={} => {}".format(user_id, users_journal_db[user_id]))

    await callback.message.edit_reply_markup(
        reply_markup=build_journal_keyboard(*[JOURNALS[ind] for ind in users_journal_db[user_id]])
    )
   # await bot.edit_message_reply_markup(
   #     chat_id=callback.message.chat.id,
   #     message_id=callback.message.message_id,
   #     reply_markup=build_journal_keyboard(*[JOURNALS[ind] for ind in users_journal_db[user_id]])
   # )


@router.callback_query(Context.selecting_journals and F.data == FINALIZE_JOURNALS_CBK)
async def finalize_journal_selection(callback: CallbackQuery, state: FSMContext):
    if isinstance(callback.message, types.InaccessibleMessage) or callback.message is None:
        logging.info(f"finalize_journal_selection: callback received broken/empty message. Ignoring the selection...")
        return

    user_id = callback.message.chat.id

    if user_id not in users_journal_db.keys() or not users_journal_db[user_id]:
        await callback.answer(text="No options selected!")
        return

    logging.info("User: {} => selected journals: {}".format(user_id, users_journal_db[user_id]))

    await callback.answer(text="Selection finalized!")
    await callback.message.answer(LEXICON[FINALIZE_JOURNALS_CBK])
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

    await message.answer(
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

    await callback.message.edit_reply_markup(
        reply_markup=build_keyboard(keywords, keywords, FINALIZE_KEYWORDS_TEXT, FINALIZE_KEYWORDS_CBK)
    )


@router.errors()
class MyHandler(ErrorHandler):
    async def handle(self):
       # vv = vars(self)
       # #print(vv)
       # for v in vv.items():
       #     print(v)
       # print(type(self.event.exception).__name__)
        bot_err_logger.error("Some error "+str(type(self.event.exception).__name__)+" "+str(self.event.exception))
        #pass
       # bot_err_logger.error("Some error "+str(self.exception_name)+" "+str(self.event.exception))

@router.callback_query(Context.waiting_for_keywords and F.data == FINALIZE_KEYWORDS_CBK)
async def finalize_keywords_selection(callback: CallbackQuery, state: FSMContext):
    if isinstance(callback.message, types.InaccessibleMessage) or callback.message is None:
        logging.info(f"finalize_keywords_selection: callback received broken/empty message. Ignoring the selection...")
        return

    user_id = callback.message.chat.id
    
    logging.info("User: {} => selected keywords: {}".format(user_id, users_keywords_db[user_id]))

    if user_id not in users_keywords_db.keys() or not users_keywords_db[user_id]:
        await callback.answer(text="Please, submit at least 1 keyword!")
        return

    await callback.answer(text="Keywords selection finalized!")
    await callback.message.answer(LEXICON[FINALIZE_KEYWORDS_CBK])
    await state.clear()
