# https://github.com/Infamous-Hydra/YaeMiko
# https://github.com/Team-ProjectCodeX

# <============================================== IMPORTS =========================================================>
import asyncio
import contextlib
import importlib
import json
import re
import time
import traceback
from platform import python_version
from random import choice

import psutil
import pyrogram
import telegram
import telethon
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.error import (
    BadRequest,
    ChatMigrated,
    Forbidden,
    NetworkError,
    TelegramError,
    TimedOut,
)
from telegram.ext import (
    ApplicationHandlerStop,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram.helpers import escape_markdown

from Infamous.karma import *
from Mikobot import (
    BOT_NAME,
    LOGGER,
    OWNER_ID,
    SUPPORT_CHAT,
    TOKEN,
    StartTime,
    app,
    dispatcher,
    function,
    loop,
    tbot,
)
from Mikobot.plugins import ALL_MODULES
from Mikobot.plugins.helper_funcs.chat_status import is_user_admin
from Mikobot.plugins.helper_funcs.misc import paginate_modules

# <=======================================================================================================>

PYTHON_VERSION = python_version()
PTB_VERSION = telegram.__version__
PYROGRAM_VERSION = pyrogram.__version__
TELETHON_VERSION = telethon.__version__


# <============================================== FUNCTIONS =========================================================>
def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time


IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []
CHAT_SETTINGS = {}
USER_SETTINGS = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("Mikobot.plugins." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if imported_module.__mod_name__.lower() not in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("Can't have two modules with the same name! Please change one")

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module


# do not async
async def send_help(chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    await dispatcher.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=keyboard,
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    message = update.effective_message
    uptime = get_readable_time((time.time() - StartTime))
    if update.effective_chat.type == "private":
        if len(args) >= 1:
            if args[0].lower() == "help":
                await send_help(update.effective_chat.id, HELP_STRINGS)
            elif args[0].lower().startswith("ghelp_"):
                mod = args[0].lower().split("_", 1)[1]
                if not HELPABLE.get(mod, False):
                    return
                await send_help(
                    update.effective_chat.id,
                    HELPABLE[mod].__help__,
                    InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="ᐸ", callback_data="help_back")]]
                    ),
                )

            elif args[0].lower() == "markdownhelp":
                IMPORTED["exᴛʀᴀs"].markdown_help_sender(update)
            elif args[0].lower().startswith("stngs_"):
                match = re.match("stngs_(.*)", args[0].lower())
                chat = dispatcher.bot.getChat(match.group(1))

                if is_user_admin(chat, update.effective_user.id):
                    send_settings(match.group(1), update.effective_user.id, False)
                else:
                    send_settings(match.group(1), update.effective_user.id, True)

            elif args[0][1:].isdigit() and "rules" in IMPORTED:
                await IMPORTED["rules"].send_rules(update, args[0], from_pm=True)

        else:
            first_name = update.effective_user.first_name
            lol = await message.reply_photo(
                photo=str(choice(START_IMG)),
                caption=FIRST_PART_TEXT.format(escape_markdown(first_name)),
                parse_mode=ParseMode.MARKDOWN,
            )
            await asyncio.sleep(0.2)
            guu = await update.effective_message.reply_text("👾")
            await asyncio.sleep(1.8)
            await guu.delete()  # Await this line
            await update.effective_message.reply_text(
                PM_START_TEXT,
                reply_markup=InlineKeyboardMarkup(START_BTN),
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=False,
            )
    else:
        await message.reply_photo(
            photo=str(choice(START_IMG)),
            reply_markup=InlineKeyboardMarkup(GROUP_START_BTN),
            caption="<b>𝖨 𝖺𝗆 𝖠𝗅𝗂𝗏𝖾!</b>\n\n<b>𝖲𝗂𝗇𝖼𝖾​:</b> <code>{}</code>".format(
                uptime
            ),
            parse_mode=ParseMode.HTML,
        )


async def extra_command_handlered(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [
            InlineKeyboardButton("𝖬𝖺𝗇𝖺𝗀𝖾𝗆𝖾𝗇𝗍", callback_data="help_back"),
            InlineKeyboardButton("𝖠𝖨", callback_data="ai_command_handler"),
        ],
        [
            InlineKeyboardButton("𝖭𝗑𝗂𝗏𝗆 𝖠𝗇𝗂𝗆𝖾", callback_data="anime_command_handler"),
            InlineKeyboardButton("𝖡𝗅𝗈𝗈𝖽𝗌", callback_data="genshin_command_handler"),
        ],
        [
            InlineKeyboardButton("𝖧𝗈𝗆𝖾", callback_data="Miko_back"),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "𝖯𝗅𝖾𝖺𝗌𝖾 𝖼𝗁𝗈𝗈𝗌𝖾 𝗍𝗁𝖾 [𝗌𝖾𝗀𝗆𝖾𝗇𝗍](https://telegra.ph/file/8c092f4e9d303f9497c83.jpg) 𝗍𝗁𝖺𝗍 𝗒𝗈𝗎 𝗐𝖺𝗇𝗍 𝗍𝗈 𝖺𝖼𝖼𝖾𝗌𝗌",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


async def extra_command_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "extra_command_handler":
        await query.answer()  # Use 'await' for asynchronous calls
        await query.message.edit_text(
            "𝖯𝗅𝖾𝖺𝗌𝖾 𝖼𝗁𝗈𝗈𝗌𝖾 𝗍𝗁𝖾 [𝗌𝖾𝗀𝗆𝖾𝗇𝗍](https://telegra.ph/file/8c092f4e9d303f9497c83.jpg) 𝗍𝗁𝖺𝗍 𝗒𝗈𝗎 𝗐𝖺𝗇𝗍 𝗍𝗈 𝖺𝖼𝖼𝖾𝗌𝗌",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("𝖬𝖺𝗇𝖺𝗀𝖾𝗆𝖾𝗇𝗍", callback_data="help_back"),
                        InlineKeyboardButton("𝖠𝖨", callback_data="ai_command_handler"),
                    ],
                    [
                        InlineKeyboardButton(
                            "𝖭𝗑𝗂𝗏𝗆 𝖠𝗇𝗂𝗆𝖾", callback_data="anime_command_handler"
                        ),
                        InlineKeyboardButton(
                            "𝖡𝗅𝗈𝗈𝖽𝗌", callback_data="genshin_command_handler"
                        ),
                    ],
                    [
                        InlineKeyboardButton("𝖧𝗈𝗆𝖾", callback_data="Miko_back"),
                    ],
                ]
            ),
            parse_mode="Markdown",  # Added this line to explicitly specify Markdown parsing
        )


async def ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("𝖠𝖨", callback_data="ai_handler"),
            InlineKeyboardButton("𝖨𝗆𝖺𝗀𝖾 𝖦𝖾𝗇", callback_data="more_aihandlered"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        " *𝖧𝖾𝗋𝖾 𝖺𝗋𝖾 𝗍𝗁𝖾 𝗈𝗉𝗍𝗂𝗈𝗇𝗌 𝖿𝗈𝗋* [𝖸𝖺𝗆𝖺𝗍𝗈 𝖲𝖺𝗇](https://telegra.ph/file/ed2d9c3693cacc9b0464e.jpg):",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


async def ai_command_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "ai_command_handler":
        await query.answer()
        await query.message.edit_text(
            " *𝖧𝖾𝗋𝖾 𝖺𝗋𝖾 𝗍𝗁𝖾 𝗈𝗉𝗍𝗂𝗈𝗇𝗌 𝖿𝗈𝗋* [𝖸𝖺𝗆𝖺𝗍𝗈 𝖲𝖺𝗇](https://telegra.ph/file/ed2d9c3693cacc9b0464e.jpg):",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("𝖠𝖨", callback_data="ai_handler"),
                        InlineKeyboardButton(
                            "𝖨𝗆𝖺𝗀𝖾 𝖦𝖾𝗇", callback_data="more_aihandlered"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "𝖡𝖺𝖼𝗄", callback_data="extra_command_handler"
                        ),
                    ],
                ]
            ),
            parse_mode="Markdown",
        )


async def ai_handler_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "ai_handler":
        await query.answer()
        await query.message.edit_text(
            "[𝖠𝗋𝗍𝗂𝖿𝗂𝖼𝗂𝖺𝗅 𝖨𝗇𝗍𝖾𝗅𝗅𝗂𝗀𝖾𝗇𝖼𝖾 𝖥𝗎𝗇𝖼𝗍𝗂𝗈𝗇𝗌](https://telegra.ph/file/01a2e0cd1b9d03808c546.jpg):\n\n"
            "𝖠𝗅𝗅 𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌:\n"
            "╭• /askgpt <write query>: A chatbot using GPT for responding to user queries.\n\n"
            "╭• /palm <write prompt>: Performs a Palm search using a chatbot.\n\n"
            "╭• /upscale <reply to image>: Upscales your image quality.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "𝖬𝗈𝗋𝖾 𝖨𝗆𝖺𝗀𝖾 𝖦𝖾𝗇", callback_data="more_ai_handler"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "𝖡𝖺𝖼𝗄", callback_data="ai_command_handler"
                        ),
                    ],
                ],
            ),
            parse_mode="Markdown",
        )


async def more_ai_handler_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "more_ai_handler":
        await query.answer()
        await query.message.edit_text(
            "*𝖧𝖾𝗋𝖾𝗌 𝗆𝗈𝗋𝖾 𝗂𝗆𝖺𝗀𝖾 𝗀𝖾𝗇 𝗋𝖾𝗅𝖺𝗍𝖾𝖽 𝖼𝗈𝗆𝗆𝖺𝗇𝖽*:\n\n"
            "╭•Command: /meinamix\n"
            "  • Description: Generates an image using the meinamix model.\n\n"
            "╭•Command: /darksushi\n"
            "  • Description: Generates an image using the darksushi model.\n\n"
            "╭•Command: /meinahentai\n"
            "  • Description: Generates an image using the meinahentai model.\n\n"
            "╭•Command: /darksushimix\n"
            "  • Description: Generates an image using the darksushimix model.\n\n"
            "╭•Command: /anylora\n"
            "  • Description: Generates an image using the anylora model.\n\n"
            "╭•Command: /cetsumix\n"
            "  • Description: Generates an image using the cetsumix model.\n\n"
            "╭•Command: /anything\n"
            "  • Description: Generates an image using the anything model.\n\n"
            "╭•Command: /absolute\n"
            "  • Description: Generates an image using the absolute model.\n\n"
            "╭•Command: /darkv2\n"
            "  • Description: Generates an image using the darkv2 model.\n\n"
            "╭•Command: /creative\n"
            "  • Description: Generates an image using the creative model.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("𝖡𝖺𝖼𝗄", callback_data="ai_handler"),
                    ],
                ],
            ),
        )


async def more_aihandlered_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "more_aihandlered":
        await query.answer()
        await query.message.edit_text(
            "*𝖧𝖾𝗋𝖾𝗌 𝗆𝗈𝗋𝖾 𝗂𝗆𝖺𝗀𝖾 𝗀𝖾𝗇 𝗋𝖾𝗅𝖺𝗍𝖾𝖽 𝖼𝗈𝗆𝗆𝖺𝗇𝖽*:\n\n"
            "*Command*: /meinamix\n"
            "  • Description: Generates an image using the meinamix model.\n\n"
            "*Command*: /darksushi\n"
            "  • Description: Generates an image using the darksushi model.\n\n"
            "*Command*: /meinahentai\n"
            "  • Description: Generates an image using the meinahentai model.\n\n"
            "*Command*: /darksushimix\n"
            "  • Description: Generates an image using the darksushimix model.\n\n"
            "*Command*: /anylora\n"
            "  • Description: Generates an image using the anylora model.\n\n"
            "*Command*: /cetsumix\n"
            "  • Description: Generates an image using the cetsumix model.\n\n"
            "*Command*: /anything\n"
            "  • Description: Generates an image using the anything model.\n\n"
            "*Command*: /absolute\n"
            "  • Description: Generates an image using the absolute model.\n\n"
            "*Command*: /darkv2\n"
            "  • Description: Generates an image using the darkv2 model.\n\n"
            "*Command*: /creative\n"
            "  • Description: Generates an image using the creative model.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "𝖡𝖺𝖼𝗄", callback_data="ai_command_handler"
                        ),
                    ],
                ],
            ),
        )


async def anime_command_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "anime_command_handler":
        await query.answer()
        await query.message.edit_text(
            "⛩[𝖭𝗑𝗂𝗏𝗆 𝖠𝗇𝗂𝗆𝖾](https://i.ibb.co/vVmcvVJ/file-1047.jpg) :\n\n"
            "𝖱𝖾𝗌𝖾𝗋𝗏𝖾𝖽 𝖿𝗈𝗋 𝗌𝗈𝗆𝖾𝗍𝗁𝗂𝗇𝗀 𝗌𝗉𝖾𝖼𝗂𝖺𝗅 𝖼𝗈𝗆𝗂𝗇𝗀 𝗌𝗈𝗈𝗇 𝗂𝗇 𝗎𝗉𝖽𝖺𝗍𝖾𝗌",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("𝖬𝗈𝗋𝖾 𝖨𝗇𝖿𝗈", url="https://𝗍.𝗆𝖾/𝖠𝗅𝖼𝗒𝗈𝗇𝖾𝖡𝗈𝗍𝗌"),
                        InlineKeyboardButton(
                            "𝖭𝗑𝗂𝗏𝗆 𝖠𝗇𝗂𝗆𝖾", url="𝗁𝗍𝗍𝗉𝗌://𝗍.𝗆𝖾/𝖭𝗑𝗂𝗏𝗆_𝖭𝖾𝗍𝗐𝗈𝗋𝗄"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "𝖡𝖺𝖼𝗄", callback_data="extra_command_handler"
                        ),
                    ],
                ]
            ),
            parse_mode="Markdown",  # Added this line to explicitly specify Markdown parsing
        )


async def genshin_command_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "genshin_command_handler":
        await query.answer()
        await query.message.edit_text(
            "🍀 [𝖳𝖾𝖺𝗆 𝖡𝗅𝗈𝗈𝖽𝗌](https://i.ibb.co/6nwRVn8/file-1046.jpg) 🍀\n\n"
            "*𝖢𝗈𝗆𝗂𝗇𝗀 𝗌𝗈𝗈𝗇 𝗂𝗇 𝖺𝖿𝗍𝖾𝗋 𝗎𝗉𝖽𝖺𝗍𝖾𝗌*",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "𝖬𝗈𝗋𝖾 𝖨𝗇𝖿𝗈", url="https://t.me/Team_Bloods"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            "𝖡𝖺𝖼𝗄", callback_data="extra_command_handler"
                        ),
                    ],
                ]
            ),
            parse_mode="Markdown",  # Added this line to explicitly specify Markdown parsing
        )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    LOGGER.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    message = (
        "An exception was raised while handling an update\n"
        "<pre>update = {}</pre>\n\n"
        "<pre>{}</pre>"
    ).format(
        html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False)),
        html.escape(tb),
    )

    if len(message) >= 4096:
        message = message[:4096]
    # Finally, send the message
    await context.bot.send_message(
        chat_id=OWNER_ID, text=message, parse_mode=ParseMode.HTML
    )


# for test purposes
async def error_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    error = context.error
    try:
        raise error
    except Forbidden:
        print("no nono1")
        print(error)
        # remove update.message.chat_id from conversation list
    except BadRequest:
        print("no nono2")
        print("BadRequest caught")
        print(error)

        # handle malformed requests - read more below!
    except TimedOut:
        print("no nono3")
        # handle slow connection problems
    except NetworkError:
        print("no nono4")
        # handle other connection problems
    except ChatMigrated as err:
        print("no nono5")
        print(err)
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        print(error)
        # handle all other telegram related errors


async def help_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)

    print(query.message.chat.id)

    try:
        if mod_match:
            module = mod_match.group(1)
            text = (
                "*╭• 𝖧𝖾𝗅𝗉 𝗌𝖾𝖼𝗍𝗂𝗈𝗇 𝗈𝖿* *{}* :\n".format(HELPABLE[module].__mod_name__)
                + HELPABLE[module].__help__
            )
            await query.message.edit_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="ᐸ", callback_data="help_back")]]
                ),
            )

        elif prev_match:
            curr_page = int(prev_match.group(1))
            await query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(curr_page - 1, HELPABLE, "help")
                ),
            )

        elif next_match:
            next_page = int(next_match.group(1))
            await query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page + 1, HELPABLE, "help")
                ),
            )

        elif back_match:
            await query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, HELPABLE, "help")
                ),
            )

        await context.bot.answer_callback_query(query.id)

    except BadRequest:
        pass


async def stats_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "insider_":
        uptime = get_readable_time((time.time() - StartTime))
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent
        text = f"""
𝖵𝖯𝖲 𝖲𝗍𝖺𝗍𝗌 𝗈𝖿 𝖸𝖺𝗆𝖺𝗍𝗈 𝖲𝖺𝗇 𝖻𝗈𝗍
➖➖➖➖➖➖
𝖴𝗉𝗍𝗂𝗆𝖾 ╭• {uptime}
𝖢𝗉𝗎 ╭• {cpu}%
𝖱𝖺𝗆 ╭• {mem}%
𝖣𝗂𝗌𝗄 ╭• {disk}%

𝖯𝗒𝗍𝗁𝗈𝗇 ╭• {PYTHON_VERSION}

𝖯𝖳𝖯 ╭• {PTB_VERSION}
𝖳𝖾𝗅𝖾𝗍𝗁𝗈𝗇 ╭• {TELETHON_VERSION}
𝖯𝗒𝗋𝗈𝗀𝗋𝖺𝗆 ╭• {PYROGRAM_VERSION}
"""
        await query.answer(text=text, show_alert=True)


async def gitsource_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "𝖮𝗍𝗁𝖾𝗋 𝖡𝗈𝗍𝗌":
        source_link = "https://𝗍.𝗆𝖾/𝖠𝗅𝖼𝗒𝗈𝗇𝖾 𝖡𝗈𝗍𝗌"
        message_text = (
            f"*𝖢𝗁𝖾𝖼𝗄 𝗈𝗎𝗍 𝗈𝗎𝗋 𝗈𝗍𝗁𝖾𝗋 𝖻𝗈𝗍𝗌!!*:\n\n{source_link}"
        )

        # Adding the inline button
        keyboard = [[InlineKeyboardButton(text="ᐸ", callback_data="Miko_back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            message_text,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
            reply_markup=reply_markup,
        )


async def bots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    source_link = "𝗁𝗍𝗍𝗉𝗌://𝗍.𝗆𝖾/𝖺𝗅𝖼𝗒𝗈𝗇𝖾𝖻𝗈𝗍𝗌"
    message_text = f"*𝖢𝗁𝖾𝖼𝗄 𝗈𝗎𝗍 𝗈𝗎𝗋 𝗈𝗍𝗁𝖾𝗋 𝖻𝗈𝗍𝗌 𝗁𝖾𝗋𝖾*:\n\n{source_link}"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message_text,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=False,
    )


async def Miko_about_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "Miko_":
        uptime = get_readable_time((time.time() - StartTime))
        message_text = (
            f"╭• <b>𝖠𝗋𝗍𝗂𝖿𝗂𝖼𝖺𝗅 𝖨𝗇𝗍𝖾𝗅𝗅𝗂𝗀𝖾𝗇𝖼𝖾 𝖨𝗇𝗍𝖾𝗀𝗋𝖺𝗍𝖾𝖽.</b>"
            f"\n╭• <b>𝖠𝖽𝗏𝖺𝗇𝖼𝖾 𝖬𝖺𝗇𝖺𝗀𝖾𝗆𝖾𝗇𝗍 𝖢𝖺𝗉𝖺𝖻𝗂𝗅𝗂𝗍𝗂𝖾𝗌.</b>"
            f"\n╭• <b>𝖠𝗇𝗂𝗆𝖾 𝖭𝖾𝗍𝗐𝗈𝗋𝗄 𝖺𝗇𝖽 𝖡𝗅𝗈𝗈𝖽𝗌.</b>"
            f"\n\n<b>𝖢𝗅𝗂𝖼𝗄 𝗈𝗇 𝗍𝗁𝖾 𝖻𝗎𝗍𝗍𝗈𝗇𝗌 𝖻𝖾𝗅𝗈𝗐 𝖿𝗈𝗋 𝗁𝖾𝗅𝗉 𝖺𝗇𝖽 𝗂𝗇𝖿𝗈 𝖺𝖻𝗈𝗎𝗍</b> {BOT_NAME}."
        )
        await query.message.edit_text(
            text=message_text,
            disable_web_page_preview=True,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="𝖠𝖻𝗈𝗎𝗍", callback_data="Miko_support"
                        ),
                        InlineKeyboardButton(text="𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌", callback_data="help_back"),
                    ],
                    [
                        InlineKeyboardButton(text="𝖲𝗍𝖺𝗍𝗂𝗌𝗍𝗂𝖼𝗌", callback_data="insider_"),
                    ],
                    [
                        InlineKeyboardButton(text="ᐸ", callback_data="Miko_back"),
                    ],
                ]
            ),
        )
    elif query.data == "Miko_support":
        message_text = (
            "𝖮𝗉𝗍𝗂𝗆𝗂𝗓𝖾𝖽 𝖿𝗈𝗋 𝖾𝖿𝖿𝗂𝖼𝗂𝖾𝗇𝖼𝗒, 𝗈𝗎𝗋 𝖻𝗈𝗍 𝗎𝗍𝗂𝗅𝗂𝗓𝖾𝗌 𝖲𝖰𝖫, 𝖬𝗈𝗇𝗀𝗈𝖣𝖡, 𝖠𝖯𝖨𝗌, 𝖺𝗇𝖽 𝖬𝖳𝖯𝗋𝗈𝗍𝗈 𝗍𝗈 𝖾𝗇𝗌𝗎𝗋𝖾 𝗌𝖾𝖼𝗎𝗋𝖾, 𝗋𝖺𝗉𝗂𝖽, 𝖺𝗇𝖽 𝗋𝖾𝗅𝗂𝖺𝖻𝗅𝖾 𝗈𝗉𝖾𝗋𝖺𝗍𝗂𝗈𝗇𝗌 𝗋𝗎𝗇𝗇𝗂𝗇𝗀 𝗈𝗇 𝖺 𝗁𝗂𝗀𝗁-𝗉𝖾𝗋𝖿𝗈𝗋𝗆𝖺𝗇𝖼𝖾 𝗌𝖾𝗋𝗏𝖾𝗋."
            f"\n\n𝖨𝖿 𝗒𝗈𝗎 𝖿𝗂𝗇𝖽 𝖺𝗇𝗒 𝖻𝗎𝗀 𝗂𝗇 {BOT_NAME} 𝖯𝗅𝖾𝖺𝗌𝖾 𝗋𝖾𝗉𝗈𝗋𝗍 𝗂𝗍 𝖺𝗍 𝗍𝗁𝖾 𝗌𝗎𝗉𝗉𝗈𝗋𝗍 𝖼𝗁𝖺𝗍."
        )
        await query.message.edit_text(
            text=message_text,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="𝖲𝗎𝗉𝗉𝗈𝗋𝗍", url=f"https://t.me/{SUPPORT_CHAT}"
                        ),
                        InlineKeyboardButton(
                            text="𝖣𝖾𝗏𝖾𝗅𝗈𝗉𝖾𝗋", url=f"tg://user?id={OWNER_ID}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(text="ᐸ", callback_data="Miko_"),
                    ],
                ]
            ),
        )
    elif query.data == "Miko_back":
        first_name = update.effective_user.first_name
        await query.message.edit_text(
            PM_START_TEXT.format(escape_markdown(first_name), BOT_NAME),
            reply_markup=InlineKeyboardMarkup(START_BTN),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )


async def get_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat  # type: Optional[Chat]
    args = update.effective_message.text.split(None, 1)

    # ONLY send help in PM
    if chat.type != chat.PRIVATE:
        if len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
            module = args[1].lower()
            await update.effective_message.reply_text(
                f"Contact me in PM to get help of {module.capitalize()}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="𝖧𝖾𝗅𝗉",
                                url="https://t.me/{}?start=ghelp_{}".format(
                                    context.bot.username, module
                                ),
                            )
                        ]
                    ]
                ),
            )
            return
        await update.effective_message.reply_text(
            "𝖢𝗁𝗈𝗈𝗌𝖾 𝖺𝗇 𝗈𝗉𝗍𝗂𝗈𝗇 𝖿𝗈𝗋 𝗀𝖾𝗍𝗍𝗂𝗇𝗀 [𝗁𝖾𝗅𝗉](https://telegra.ph/file/cce9038f6a9b88eb409b5.jpg)",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="𝖮𝗉𝖾𝗇 𝗂𝗇 𝖯𝖬",
                            url="https://t.me/{}?start=help".format(
                                context.bot.username
                            ),
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="𝖮𝗉𝖾𝗇 𝗁𝖾𝗋𝖾",
                            callback_data="extra_command_handler",
                        )
                    ],
                ]
            ),
            parse_mode="Markdown",  # Added this line to explicitly specify Markdown parsing
        )
        return

    elif len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
        module = args[1].lower()
        text = (
            "𝖧𝖾𝗋𝖾 𝗂𝗌 𝗍𝗁𝖾 𝖺𝗏𝖺𝗂𝗅𝖺𝖻𝗅𝖾 𝗁𝖾𝗅𝗉 𝖿𝗈𝗋 𝗍𝗁𝖾 *{}* 𝗆𝗈𝖽𝗎𝗅𝖾:\n".format(
                HELPABLE[module].__mod_name__
            )
            + HELPABLE[module].__help__
        )
        await send_help(
            chat.id,
            text,
            InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="ᐸ", callback_data="help_back")]]
            ),
        )

    else:
        await send_help(chat.id, HELP_STRINGS)


async def send_settings(chat_id, user_id, user=False):
    if user:
        if USER_SETTINGS:
            settings = "\n\n".join(
                "*{}*:\n{}".format(mod.__mod_name__, mod.__user_settings__(user_id))
                for mod in USER_SETTINGS.values()
            )
            await dispatcher.bot.send_message(
                user_id,
                "𝖳𝗁𝖾𝗌𝖾 𝖺𝗋𝖾 𝗒𝗈𝗎𝗋 𝖼𝗎𝗋𝗋𝖾𝗇𝗍 𝗌𝖾𝗍𝗍𝗂𝗇𝗀𝗌:" + "\n\n" + settings,
                parse_mode=ParseMode.MARKDOWN,
            )

        else:
            await dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any user specific settings available :'(",
                parse_mode=ParseMode.MARKDOWN,
            )
    else:
        if CHAT_SETTINGS:
            chat_name = dispatcher.bot.getChat(chat_id).title
            await dispatcher.bot.send_message(
                user_id,
                text="Which module would you like to check {}'s settings for?".format(
                    chat_name
                ),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )
        else:
            await dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any chat settings available :'(\nSend this "
                "in a group chat you're admin in to find its current settings!",
                parse_mode=ParseMode.MARKDOWN,
            )


async def settings_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    bot = context.bot
    mod_match = re.match(r"stngs_module\((.+?),(.+?)\)", query.data)
    prev_match = re.match(r"stngs_prev\((.+?),(.+?)\)", query.data)
    next_match = re.match(r"stngs_next\((.+?),(.+?)\)", query.data)
    back_match = re.match(r"stngs_back\((.+?)\)", query.data)
    try:
        if mod_match:
            chat_id = mod_match.group(1)
            module = mod_match.group(2)
            chat = bot.get_chat(chat_id)
            text = "*{}* has the following settings for the *{}* module:\n\n".format(
                escape_markdown(chat.title), CHAT_SETTINGS[module].__mod_name__
            ) + CHAT_SETTINGS[module].__chat_settings__(chat_id, user.id)
            await query.message.reply_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="ᐸ",
                                callback_data="stngs_back({})".format(chat_id),
                            )
                        ]
                    ]
                ),
            )

        elif prev_match:
            chat_id = prev_match.group(1)
            curr_page = int(prev_match.group(2))
            chat = bot.get_chat(chat_id)
            await query.message.reply_text(
                "Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        curr_page - 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif next_match:
            chat_id = next_match.group(1)
            next_page = int(next_match.group(2))
            chat = bot.get_chat(chat_id)
            await query.message.reply_text(
                "Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        next_page + 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif back_match:
            chat_id = back_match.group(1)
            chat = bot.get_chat(chat_id)
            await query.message.reply_text(
                text="Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(escape_markdown(chat.title)),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )

        # ensure no spinny white circle
        bot.answer_callback_query(query.id)
        await query.message.delete()
    except BadRequest as excp:
        if excp.message not in [
            "Message is not modified",
            "Query_id_invalid",
            "Message can't be deleted",
        ]:
            LOGGER.exception("Exception in settings buttons. %s", str(query.data))


async def get_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]

    # ONLY send settings in PM
    if chat.type != chat.PRIVATE:
        if is_user_admin(chat, user.id):
            text = "Click here to get this chat's settings, as well as yours."
            await msg.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌",
                                url="t.me/{}?start=stngs_{}".format(
                                    context.bot.username, chat.id
                                ),
                            )
                        ]
                    ]
                ),
            )
        else:
            text = "Click here to check your settings."

    else:
        await send_settings(chat.id, user.id, True)


async def migrate_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message  # type: Optional[Message]
    if msg.migrate_to_chat_id:
        old_chat = update.effective_chat.id
        new_chat = msg.migrate_to_chat_id
    elif msg.migrate_from_chat_id:
        old_chat = msg.migrate_from_chat_id
        new_chat = update.effective_chat.id
    else:
        return

    LOGGER.info("Migrating from %s, ᴛᴏ %s", str(old_chat), str(new_chat))
    for mod in MIGRATEABLE:
        with contextlib.suppress(KeyError, AttributeError):
            mod.__migrate__(old_chat, new_chat)

    LOGGER.info("Successfully Migrated!")
    raise ApplicationHandlerStop


# <=======================================================================================================>


# <=================================================== MAIN ====================================================>
def main():
    function(CommandHandler("start", start))

    function(CommandHandler("help", extra_command_handlered))
    function(CallbackQueryHandler(help_button, pattern=r"help_.*"))

    function(CommandHandler("settings", get_settings))
    function(CallbackQueryHandler(settings_button, pattern=r"stngs_"))
    function(CommandHandler("bots", bots))

    function(CallbackQueryHandler(Miko_about_callback, pattern=r"Miko_"))
    function(CallbackQueryHandler(gitsource_callback, pattern=r"git_source"))
    function(CallbackQueryHandler(stats_back, pattern=r"insider_"))
    function(MessageHandler(filters.StatusUpdate.MIGRATE, migrate_chats))
    function(CallbackQueryHandler(ai_handler_callback, pattern=r"ai_handler"))
    function(CallbackQueryHandler(more_ai_handler_callback, pattern=r"more_ai_handler"))
    function(CallbackQueryHandler(ai_command_callback, pattern="ai_command_handler"))
    function(
        CallbackQueryHandler(anime_command_callback, pattern="anime_command_handler")
    )
    function(
        CallbackQueryHandler(more_aihandlered_callback, pattern="more_aihandlered")
    )
    function(
        CallbackQueryHandler(extra_command_callback, pattern="extra_command_handler")
    )

    function(CommandHandler("ai", ai_command))
    function(
        CallbackQueryHandler(
            genshin_command_callback, pattern="genshin_command_handler"
        )
    )

    dispatcher.add_error_handler(error_callback)

    LOGGER.info("Mikobot is starting >> Using long polling.")
    dispatcher.run_polling(timeout=15, drop_pending_updates=True)


if __name__ == "__main__":
    try:
        LOGGER.info("Successfully loaded modules: " + str(ALL_MODULES))
        tbot.start(bot_token=TOKEN)
        app.start()
        main()
    except KeyboardInterrupt:
        pass
    except Exception:
        err = traceback.format_exc()
        LOGGER.info(err)
    finally:
        try:
            if loop.is_running():
                loop.stop()
        finally:
            loop.close()
        LOGGER.info(
            "------------------------ Stopped Services ------------------------"
        )
# <==================================================== END ===================================================>
