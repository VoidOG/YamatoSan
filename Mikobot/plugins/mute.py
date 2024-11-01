import html
from typing import Union

from telegram import Bot, Chat, ChatMember, ChatPermissions, Update
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import CommandHandler, ContextTypes
from telegram.helpers import mention_html

from Mikobot import LOGGER, function
from Mikobot.plugins.helper_funcs.chat_status import (
    check_admin,
    connection_status,
    is_user_admin,
)
from Mikobot.plugins.helper_funcs.extraction import extract_user, extract_user_and_text
from Mikobot.plugins.helper_funcs.string_handling import extract_time
from Mikobot.plugins.log_channel import loggable


async def check_user(user_id: int, bot: Bot, chat: Chat) -> Union[str, None]:
    if not user_id:
        reply = "𝖸𝗈𝗎 𝖽𝗈𝗇𝗍 𝗌𝖾𝖾𝗆 𝗍𝗈 𝖻𝖾 𝗋𝖾𝖿𝖾𝗋𝗋𝗂𝗇𝗀 𝗍𝗈 𝖺 𝗎𝗌𝖾𝗋 𝗈𝗋 𝗍𝗁𝖾 𝖨𝖣 𝗌𝗉𝖾𝖼𝗂𝖿𝗂𝖾𝖽 𝗂𝗌 𝗂𝗇𝖼𝗈𝗋𝗋𝖾𝖼𝗍..."
        return reply

    try:
        member = await chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "𝖴𝗌𝖾𝗋 𝗇𝗈𝗍 𝖿𝗈𝗎𝗇𝖽":
            reply = "𝖨 𝖼𝖺𝗇𝗍 𝗌𝖾𝖾𝗆 𝗍𝗈 𝖿𝗂𝗇𝖽 𝗍𝗁𝗂𝗌 𝗎𝗌𝖾𝗋"
            return reply
        else:
            raise

    if user_id == bot.id:
        reply = "𝖨𝗆 𝗇𝗈𝗍 𝗀𝗈𝗇𝗇𝖺 𝗆𝗎𝗍𝖾 𝗆𝗒𝗌𝖾𝗅𝖿, 𝖧𝗈𝗐 𝗁𝗂𝗀𝗁 𝖺𝗋𝖾 𝗒𝗈𝗎?"
        return reply

    if await is_user_admin(chat, user_id, member):
        reply = "𝖲𝗈𝗋𝗋𝗒 𝖢𝖺𝗇'𝗍 𝖽𝗈 𝗍𝗁𝖺𝗍, 𝗍𝗁𝗂𝗌 𝗎𝗌𝖾𝗋 𝗂𝗌 𝖺𝖽𝗆𝗂𝗇 𝗁𝖾𝗋𝖾."
        return reply

    return None


@connection_status
@loggable
@check_admin(permission="can_restrict_members", is_both=True)
async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message

    user_id, reason = await extract_user_and_text(message, context, args)
    reply = await check_user(user_id, bot, chat)

    if reply:
        await message.reply_text(reply)
        return ""

    member = await chat.get_member(user_id)

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"𝖬𝗎𝗍𝖾\n"
        f"<b>𝖠𝖽𝗆𝗂𝗇:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>𝖴𝗌𝖾𝗋:</b> {mention_html(member.user.id, member.user.first_name)}"
    )

    if reason:
        log += f"\n<b>𝖱𝖾𝖺𝗌𝗈𝗇:</b> {reason}"

    if member.status in [ChatMember.RESTRICTED, ChatMember.MEMBER]:
        chat_permissions = ChatPermissions(can_send_messages=False)
        await bot.restrict_chat_member(chat.id, user_id, chat_permissions)
        await bot.sendMessage(
            chat.id,
            f"𝖬𝗎𝗍𝖾𝖽 <b>{html.escape(member.user.first_name)}</b> 𝗐𝗂𝗍𝗁 𝗇𝗈 𝖾𝗑𝗉𝗂𝗋𝖺𝗍𝗂𝗈𝗇 𝖽𝖺𝗍𝖾!",
            parse_mode=ParseMode.HTML,
            message_thread_id=message.message_thread_id if chat.is_forum else None,
        )
        return log

    else:
        await message.reply_text("𝖳𝗁𝗂𝗌 𝗎𝗌𝖾𝗋 𝗂𝗌 𝖺𝗅𝗋𝖾𝖺𝖽𝗒 𝗆𝗎𝗍𝖾𝖽")

    return ""


@connection_status
@loggable
@check_admin(permission="can_restrict_members", is_both=True)
async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    bot, args = context.bot, context.args
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message

    user_id = await extract_user(message, context, args)
    if not user_id:
        await message.reply_text(
            "𝖸𝗈𝗎 𝗐𝗂𝗅𝗅 𝗇𝖾𝖾𝖽 𝗍𝗈 𝖾𝗂𝗍𝗁𝖾𝗋 𝗀𝗂𝗏𝖾 𝗆𝖾 𝖺 𝗎𝗌𝖾𝗋𝗇𝖺𝗆𝖾 𝗍𝗈 𝗎𝗇𝗆𝗎𝗍𝖾, 𝗈𝗋 𝗋𝖾𝗉𝗅𝗒 𝗍𝗈 𝗌𝗈𝗆𝖾𝗈𝗇𝖾 𝗍𝗈 𝖻𝖾 𝗎𝗇𝗆𝗎𝗍𝖾𝖽.",
        )
        return ""

    member = await chat.get_member(int(user_id))

    if member.status not in [ChatMember.LEFT, ChatMember.BANNED]:
        if member.status != ChatMember.RESTRICTED:
            await message.reply_text("𝖳𝗁𝗂𝗌 𝗎𝗌𝖾𝗋 𝗁𝖺𝗌 𝖺𝗅𝗋𝖾𝖺𝖽𝗒 𝗍𝗁𝖾 𝗋𝗂𝗀𝗁𝗍 𝗍𝗈 𝗌𝗉𝖾𝖺𝗄.")
        else:
            chat_permissions = ChatPermissions(
                can_send_messages=True,
                can_invite_users=True,
                can_pin_messages=True,
                can_send_polls=True,
                can_change_info=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
            )
            try:
                await bot.restrict_chat_member(chat.id, int(user_id), chat_permissions)
            except BadRequest:
                pass
            await bot.sendMessage(
                chat.id,
                f"𝖨 𝗌𝗁𝖺𝗅𝗅 𝖺𝗅𝗅𝗈𝗐 <b>{html.escape(member.user.first_name)}</b> 𝗍𝗈 𝗍𝖾𝗑𝗍!",
                parse_mode=ParseMode.HTML,
                message_thread_id=message.message_thread_id if chat.is_forum else None,
            )
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"𝖴𝗇𝗆𝗎𝗍𝖾\n"
                f"<b>𝖠𝖽𝗆𝗂𝗇:</b> {mention_html(user.id, user.first_name)}\n"
                f"<b>𝖴𝗌𝖾𝗋:</b> {mention_html(member.user.id, member.user.first_name)}"
            )
    else:
        await message.reply_text(
            "𝖳𝗁𝗂𝗌 𝗎𝗌𝖾𝗋 𝗂𝗌𝗇𝗍 𝖾𝗏𝖾𝗇 𝗂𝗇 𝗍𝗁𝖾 𝖼𝗁𝖺𝗍, 𝗎𝗇𝗆𝗎𝗍𝗂𝗇𝗀 𝗍𝗁𝖾𝗆 𝗐𝗈𝗇'𝗍 𝗆𝖺𝗄𝖾 𝗍𝗁𝖾𝗆 𝗍𝖺𝗅𝗄 𝗆𝗈𝗋𝖾 𝗍𝗁𝖺𝗇 𝗍𝗁𝖾𝗒 "
            "𝖺𝗅𝗋𝖾𝖺𝖽𝗒 𝖽𝗈!",
        )

    return ""


@connection_status
@loggable
@check_admin(permission="can_restrict_members", is_both=True)
async def temp_mute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    bot, args = context.bot, context.args
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message

    user_id, reason = await extract_user_and_text(message, context, args)
    reply = await check_user(user_id, bot, chat)

    if reply:
        await message.reply_text(reply)
        return ""

    member = await chat.get_member(user_id)

    if not reason:
        await message.reply_text("𝖸𝗈𝗎 𝗁𝖺𝗏𝖾𝗇'𝗍 𝗌𝗉𝖾𝖼𝗂𝖿𝗂𝖾𝖽 𝗍𝗁𝖾 𝗍𝗂𝗆𝖾 𝗍𝗈 𝗆𝗎𝗍𝖾 𝗍𝗁𝗂𝗌 𝗎𝗌𝖾𝗋 𝖿𝗈𝗋!")
        return ""

    split_reason = reason.split(None, 1)

    time_val = split_reason[0].lower()
    if len(split_reason) > 1:
        reason = split_reason[1]
    else:
        reason = ""

    mutetime = await extract_time(message, time_val)

    if not mutetime:
        return ""

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"𝖳𝖾𝗆𝗉 𝖬𝗎𝗍𝖾𝖽\n"
        f"<b>𝖠𝖽𝗆𝗂𝗇:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>𝖴𝗌𝖾𝗋:</b> {mention_html(member.user.id, member.user.first_name)}\n"
        f"<b>𝖳𝗂𝗆𝖾:</b> {time_val}"
    )
    if reason:
        log += f"\n<b>𝖱𝖾𝖺𝗌𝗈𝗇:</b> {reason}"

    try:
        if member.status in [ChatMember.RESTRICTED, ChatMember.MEMBER]:
            chat_permissions = ChatPermissions(can_send_messages=False)
            await bot.restrict_chat_member(
                chat.id,
                user_id,
                chat_permissions,
                until_date=mutetime,
            )
            await bot.sendMessage(
                chat.id,
                f"𝖬𝗎𝗍𝖾𝖽 <b>{html.escape(member.user.first_name)}</b> 𝖿𝗈𝗋 {time_val}!",
                parse_mode=ParseMode.HTML,
                message_thread_id=message.message_thread_id if chat.is_forum else None,
            )
            return log
        else:
            await message.reply_text("𝖳𝗁𝗂𝗌 𝗎𝗌𝖾𝗋 𝗂𝗌 𝖺𝗅𝗋𝖾𝖺𝖽𝗒 𝗆𝗎𝗍𝖾𝖽")

    except BadRequest as excp:
        if excp.message == "𝖱𝖾𝗉𝗅𝗒 𝗆𝖾𝗌𝗌𝖺𝗀𝖾 𝗇𝗈𝗍 𝖿𝗈𝗎𝗇𝖽":
            # Do not reply
            await message.reply_text(f"𝖬𝗎𝗍𝖾𝖽 𝖿𝗈𝗋 {time_val}!", quote=False)
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "𝖤𝗋𝗋𝗈𝗋 𝗆𝗎𝗍𝗂𝗇𝗀 𝗎𝗌𝖾𝗋 𝖿𝗈𝗋 %s 𝗂𝗇 𝗍𝗁𝖾 𝖼𝗁𝖺𝗍 %s (%s) 𝖽𝗎𝖾 𝗍𝗈 %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            await message.reply_text("𝖶𝖾𝗅𝗅 𝖽𝖺𝗆𝗇, 𝖨 𝖼𝖺𝗇'𝗍 𝗆𝗎𝗍𝖾 𝗍𝗁𝖺𝗍 𝗎𝗌𝖾𝗋.")

    return ""


__help__ = """
╭• *𝖠𝖽𝗆𝗂𝗇𝗌 𝖮𝗇𝗅𝗒:*

╭• /mute <userhandle>: silences a user. Can also be used as a reply, muting the replied to user.

╭• /tmute <userhandle> x(m/h/d): mutes a user for x time. (via handle, or reply). `m` = `minutes`, `h` = `hours`, `d` = `days`.

╭• /unmute <userhandle>: unmutes a user. Can also be used as a reply, muting the replied to user.
"""

MUTE_HANDLER = CommandHandler("mute", mute, block=False)
UNMUTE_HANDLER = CommandHandler("unmute", unmute, block=False)
TEMPMUTE_HANDLER = CommandHandler(["tmute", "tempmute"], temp_mute, block=False)

function(MUTE_HANDLER)
function(UNMUTE_HANDLER)
function(TEMPMUTE_HANDLER)

__mod_name__ = "𝖬𝗎𝗍𝖾"
__handlers__ = [MUTE_HANDLER, UNMUTE_HANDLER, TEMPMUTE_HANDLER]
