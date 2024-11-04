# <============================================== IMPORTS =========================================================>
import os
import re
from html import escape
from random import choice

from telegram import (
    ChatMemberAdministrator,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.constants import ChatID, ChatType, ParseMode
from telegram.error import BadRequest
from telegram.ext import CommandHandler, ContextTypes
from telegram.helpers import mention_html

from Database.sql.approve_sql import is_approved
from Infamous.karma import START_IMG
from Mikobot import DEV_USERS, DRAGONS, INFOPIC, OWNER_ID, function
from Mikobot.__main__ import STATS, USER_INFO
from Mikobot.plugins.helper_funcs.chat_status import support_plus
from Mikobot.plugins.users import get_user_id

# <=======================================================================================================>


# <================================================ FUNCTION =======================================================>
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    message = update.effective_message
    args = context.args
    bot = context.bot

    def reply_with_text(text):
        return message.reply_text(text, parse_mode=ParseMode.HTML)

    head = ""
    premium = False

    reply = await reply_with_text("<code>Getting information...</code>")

    user_id = None
    user_name = None

    if len(args) >= 1:
        if args[0][0] == "@":
            user_name = args[0]
            user_id = await get_user_id(user_name)

        if not user_id:
            try:
                chat_obj = await bot.get_chat(user_name)
                userid = chat_obj.id
            except BadRequest:
                await reply_with_text(
                    "I can't get information about this user/channel/group."
                )
                return
        else:
            userid = user_id
    elif len(args) >= 1 and args[0].lstrip("-").isdigit():
        userid = int(args[0])
    elif message.reply_to_message and not message.reply_to_message.forum_topic_created:
        if message.reply_to_message.sender_chat:
            userid = message.reply_to_message.sender_chat.id
        elif message.reply_to_message.from_user:
            if message.reply_to_message.from_user.id == ChatID.FAKE_CHANNEL:
                userid = message.reply_to_message.chat.id
            else:
                userid = message.reply_to_message.from_user.id
                premium = message.reply_to_message.from_user.is_premium
    elif not message.reply_to_message and not args:
        if message.from_user.id == ChatID.FAKE_CHANNEL:
            userid = message.sender_chat.id
        else:
            userid = message.from_user.id
            premium = message.from_user.is_premium

    try:
        chat_obj = await bot.get_chat(userid)
    except (BadRequest, UnboundLocalError):
        await reply_with_text("I can't get information about this user/channel/group.")
        return

    if chat_obj.type == ChatType.PRIVATE:
        if chat_obj.username:
            head = f"<b>❉ 𝖴𝗌𝖾𝗋 𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝗍𝗂𝗈𝗇 </b>\n\n"
            if chat_obj.username.endswith("bot"):
                head = f"╭• <b>𝖡𝗈𝗍 𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝗍𝗂𝗈𝗇</b> 】⇦\n\n"

        head += f"╭• <b>𝖨𝖣:</b> <code>{chat_obj.id}</code>"
        head += f"\n╭• <b>𝖥𝗂𝗋𝗌𝗍 𝖭𝖺𝗆𝖾:</b> {chat_obj.first_name}"
        if chat_obj.last_name:
            head += f"\n╭• <b>𝖫𝖺𝗌𝗍 𝖭𝖺𝗆𝖾:</b> {chat_obj.last_name}"
        if chat_obj.username:
            head += f"\n╭• <b>𝖴𝗌𝖾𝗋𝗇𝖺𝗆𝖾:</b> @{chat_obj.username}"
        head += f"\n╭• <b>𝖯𝖾𝗋𝗆𝖺𝗇𝖾𝗇𝗍 𝖫𝗂𝗇𝗄:</b> {mention_html(chat_obj.id, 'link')}"

        if chat_obj.username and not chat_obj.username.endswith("bot"):
            head += f"\n\n╭• <b>𝖯𝗋𝖾𝗆𝗂𝗎𝗆 𝖴𝗌𝖾𝗋:</b> {premium}"

        if chat_obj.bio:
            head += f"\n\n<b>╭• 𝖡𝗂𝗈:</b> {chat_obj.bio}"

        chat_member = await chat.get_member(chat_obj.id)
        if isinstance(chat_member, ChatMemberAdministrator):
            head += f"\n╭• <b>𝖯𝗋𝖾𝗌𝖾𝗇𝖼𝖾:</b> {chat_member.status}"
            if chat_member.custom_title:
                head += f"\n╭• <b>𝖠𝖽𝗆𝗂𝗇 𝖳𝗂𝗍𝗅𝖾:</b> {chat_member.custom_title}"
        else:
            head += f"\n╭• <b>𝖯𝗋𝖾𝗌𝖾𝗇𝖼𝖾:</b> {chat_member.status}"

        if is_approved(chat.id, chat_obj.id):
            head += f"\n╭• <b>𝖠𝗉𝗉𝗋𝗈𝗏𝖾𝖽:</b> This user is approved in this chat."

        disaster_level_present = False

        if chat_obj.id == OWNER_ID:
            head += "\n\n <b>The disaster level of this person is My Owner.</b>"
            disaster_level_present = True
        elif chat_obj.id in DEV_USERS:
            head += "\n\n <b>This user is a member of Infamous Hydra.</b>"
            disaster_level_present = True
        elif chat_obj.id in DRAGONS:
            head += "\n\n <b>The disaster level of this person is Dragon.</b>"
            disaster_level_present = True
        if disaster_level_present:
            head += " [?]"

        for mod in USER_INFO:
            try:
                mod_info = mod.__user_info__(chat_obj.id).strip()
            except TypeError:
                mod_info = mod.__user_info__(chat_obj.id, chat.id).strip()

            head += "\n\n" + mod_info if mod_info else ""

    if chat_obj.type == ChatType.SENDER:
        head = f"𝖲𝖾𝗇𝖽𝖾𝗋 𝖢𝗁𝖺𝗍 𝖨𝗇𝖿𝗈𝗋𝗆𝖺𝗍𝗂𝗈𝗇:\n"
        await reply_with_text("Found sender chat, getting information...")
        head += f"<b>𝖨𝖣:</b> <code>{chat_obj.id}</code>"
        if chat_obj.title:
            head += f"\ <b>Title:</b> {chat_obj.title}"
        if chat_obj.username:
            head += f"\ <b>Username:</b> @{chat_obj.username}"
        head += f"\n Permalink: {mention_html(chat_obj.id, 'link')}"
        if chat_obj.description:
            head += f"\n <b>Description:</b> {chat_obj.description}"

    elif chat_obj.type == ChatType.CHANNEL:
        head = f"Channel Information:\n"
        await reply_with_text("Found channel, getting information...")
        head += f"<b>ID:</b> <code>{chat_obj.id}</code>"
        if chat_obj.title:
            head += f"\n<b>Title:</b> {chat_obj.title}"
        if chat_obj.username:
            head += f"\n<b>Username:</b> @{chat_obj.username}"
        head += f"\nPermalink: {mention_html(chat_obj.id, 'link')}"
        if chat_obj.description:
            head += f"\n<b>Description:</b> {chat_obj.description}"
        if chat_obj.linked_chat_id:
            head += f"\n<b>Linked Chat ID:</b> <code>{chat_obj.linked_chat_id}</code>"

    elif chat_obj.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        head = f"Group Information:\n"
        await reply_with_text("Found group, getting information...")
        head += f"<b>ID:</b> <code>{chat_obj.id}</code>"
        if chat_obj.title:
            head += f"\n<b>Title:</b> {chat_obj.title}"
        if chat_obj.username:
            head += f"\n<b>Username:</b> @{chat_obj.username}"
        head += f"\nPermalink: {mention_html(chat_obj.id, 'link')}"
        if chat_obj.description:
            head += f"\n<b>Description:</b> {chat_obj.description}"

    if INFOPIC:
        try:
            if chat_obj.photo:
                _file = await chat_obj.photo.get_big_file()
                await _file.download_to_drive(f"{chat_obj.id}.png")
                await message.reply_photo(
                    photo=open(f"{chat_obj.id}.png", "rb"),
                    caption=(head),
                    parse_mode=ParseMode.HTML,
                )
                await reply.delete()
                os.remove(f"{chat_obj.id}.png")
            else:
                await reply_with_text(escape(head))
        except:
            await reply_with_text(escape(head))


@support_plus
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats = " <b>𝖸𝖺𝗆𝖺𝗍𝗈 𝖲𝖺𝗇'𝗌 𝖲𝗍𝖺𝗍𝗂𝗌𝗍𝗂𝖼𝗌:</b>\n\n" + "\n".join(
        [mod.__stats__() for mod in STATS]
    )
    result = re.sub(r"(\d+)", r"<code>\1</code>", stats)

    keyboard = [
        [
            InlineKeyboardButton(
                "𝖠𝗅𝖼𝗒𝗈𝗇𝖾 𝖡𝗈𝗍𝗌", url="https://t.me/𝖠𝗅𝖼𝗒𝗈𝗇𝖾𝖡𝗈𝗍𝗌"
            ),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.effective_message.reply_photo(
        photo=str(choice(START_IMG)),
        caption=result,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup,
    )


# <=================================================== HELP ====================================================>


__help__ = """
*𝖮𝗏𝖾𝗋𝖺𝗅𝗅 𝗂𝗇𝖿𝗈𝗋𝗆𝖺𝗍𝗂𝗈𝗇 𝖺𝖻𝗈𝗎𝗍 𝖺 𝗎𝗌𝖾𝗋:*

» /info : 𝖥𝖾𝗍𝖼𝗁 𝗎𝗌𝖾𝗋 𝗂𝗇𝖿𝗈𝗋𝗆𝖺𝗍𝗂𝗈𝗇.
"""

# <================================================ HANDLER =======================================================>
STATS_HANDLER = CommandHandler(["stats", "gstats"], stats, block=False)
INFO_HANDLER = CommandHandler(("info", "book"), info, block=False)

function(STATS_HANDLER)
function(INFO_HANDLER)

__mod_name__ = "𝖨𝗇𝖿𝗈"
__command_list__ = ["info"]
__handlers__ = [INFO_HANDLER, STATS_HANDLER]
# <================================================ END =======================================================>
