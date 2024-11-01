# <============================================== IMPORTS =========================================================>
from asyncio import sleep

from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.errors import MessageDeleteForbidden, RPCError
from pyrogram.types import Message

from Mikobot import SUPPORT_CHAT, app
from Mikobot.utils.can_restrict import can_restrict

# <=======================================================================================================>


# <================================================ FUNCTION =======================================================>
@app.on_message(filters.command("purge"))
@can_restrict
async def purge(c: app, m: Message):
    if m.chat.type != ChatType.SUPERGROUP:
        await m.reply_text(text="𝖢𝖺𝗇𝗇𝗈𝗍 𝗉𝗎𝗋𝗀𝖾 𝗆𝖾𝗌𝗌𝖺𝗀𝖾 𝗂𝗇 𝖺 𝖻𝖺𝗌𝗂𝖼 𝗀𝗋𝗈𝗎𝗉")
        return

    if m.reply_to_message:
        message_ids = list(range(m.reply_to_message.id, m.id))

        def divide_chunks(l: list, n: int = 100):
            for i in range(0, len(l), n):
                yield l[i : i + n]

        # Dielete messages in chunks of 100 messages
        m_list = list(divide_chunks(message_ids))

        try:
            for plist in m_list:
                await c.delete_messages(
                    chat_id=m.chat.id,
                    message_ids=plist,
                    revoke=True,
                )
            await m.delete()
        except MessageDeleteForbidden:
            await m.reply_text(
                text="𝖢𝖺𝗇𝗇𝗈𝗍 𝖽𝖾𝗅𝖾𝗍𝖾 𝖺𝗅𝗅 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌. 𝖳𝗁𝖾 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝗆𝖺𝗒𝖻𝖾 𝗍𝗈𝗈 𝗈𝗅𝖽, 𝖨 𝗆𝗂𝗀𝗁𝗍 𝗇𝗈𝗍 𝗁𝖺𝗏𝖾 𝖽𝖾𝗅𝖾𝗍𝖾 𝗋𝗂𝗀𝗁𝗍𝗌, 𝗈𝗋 𝗍𝗁𝗂𝗌 𝗆𝗂𝗀𝗁𝗍 𝗇𝗈𝗍 𝖻𝖾 𝖺 𝗌𝗎𝗉𝖾𝗋𝗀𝗋𝗈𝗎𝗉."
            )
            return
        except RPCError as ef:
            await m.reply_text(
                text=f"""𝖲𝗈𝗆𝖾 𝖾𝗋𝗋𝗈𝗋 𝗈𝖼𝖼𝗎𝗋𝖾𝖽, 𝗋𝖾𝗉𝗈𝗋𝗍 𝗍𝗈 @{SUPPORT_CHAT}

      <b>Error:</b> <code>{ef}</code>"""
            )

        count_del_msg = len(message_ids)

        z = await m.reply_text(text=f"𝖣𝖾𝗅𝖾𝗍𝖾𝖽 <i>{count_del_msg}</i> 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌")
        await sleep(3)
        await z.delete()
        return
    await m.reply_text("𝖱𝖾𝗉𝗒 𝗍𝗈 𝖺 𝗆𝖾𝗌𝗌𝖺𝗀𝖾 𝗍𝗈 𝗌𝗍𝖺𝗋𝗍 𝗉𝗎𝗋𝗀𝖾!")
    return


@app.on_message(filters.command("spurge"))
@can_restrict
async def spurge(c: app, m: Message):
    if m.chat.type != ChatType.SUPERGROUP:
        await m.reply_text(text="𝖢𝖺𝗇𝗇𝗈𝗍 𝗉𝗎𝗋𝗀𝖾 𝗆𝖾𝗌𝗌𝖺𝗀𝖾 𝗂𝗇 𝖺 𝖻𝖺𝗌𝗂𝖼 𝗀𝗋𝗈𝗎𝗉")
        return

    if m.reply_to_message:
        message_ids = list(range(m.reply_to_message.id, m.id))

        def divide_chunks(l: list, n: int = 100):
            for i in range(0, len(l), n):
                yield l[i : i + n]

        # Dielete messages in chunks of 100 messages
        m_list = list(divide_chunks(message_ids))

        try:
            for plist in m_list:
                await c.delete_messages(
                    chat_id=m.chat.id,
                    message_ids=plist,
                    revoke=True,
                )
            await m.delete()
        except MessageDeleteForbidden:
            await m.reply_text(
                text="𝖢𝖺𝗇𝗇𝗈𝗍 𝖽𝖾𝗅𝖾𝗍𝖾 𝖺𝗅𝗅 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌. 𝖳𝗁𝖾 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝗆𝖺𝗒𝖻𝖾 𝗍𝗈𝗈 𝗈𝗅𝖽, 𝖨 𝗆𝗂𝗀𝗁𝗍 𝗇𝗈𝗍 𝗁𝖺𝗏𝖾 𝖽𝖾𝗅𝖾𝗍𝖾 𝗋𝗂𝗀𝗁𝗍𝗌, 𝗈𝗋 𝗍𝗁𝗂𝗌 𝗆𝗂𝗀𝗁𝗍 𝗇𝗈𝗍 𝖻𝖾 𝖺 𝗌𝗎𝗉𝖾𝗋𝗀𝗋𝗈𝗎𝗉."
            )
            return
        except RPCError as ef:
            await m.reply_text(
                text=f"""𝖲𝗈𝗆𝖾 𝖾𝗋𝗋𝗈𝗋 𝗈𝖼𝖼𝗎𝗋𝖾𝖽, 𝗋𝖾𝗉𝗈𝗋𝗍 𝗍𝗈 @{SUPPORT_CHAT}

      <b>Error:</b> <code>{ef}</code>"""
            )
        return
    await m.reply_text("𝖱𝖾𝗉𝗅𝗒 𝗍𝗈 𝖺 𝗆𝖾𝗌𝗌𝖺𝗀𝖾 𝗍𝗈 𝗌𝗍𝖺𝗋𝗍 𝗉𝗎𝗋𝗀𝖾")
    return


@app.on_message(
    filters.command("del"),
    group=9,
)
@can_restrict
async def del_msg(c: app, m: Message):
    if m.chat.type != ChatType.SUPERGROUP:
        return

    if m.reply_to_message:
        await m.delete()
        await c.delete_messages(
            chat_id=m.chat.id,
            message_ids=m.reply_to_message.id,
        )
    else:
        await m.reply_text(text="𝖶𝗁𝖺𝗍 𝖽𝗈 𝗒𝗈𝗎 𝗐𝖺𝗇𝗇𝖺 𝖽𝖾𝗅𝖾𝗍𝖾")
    return


# <=================================================== HELP ====================================================>
__help__ = """
╭• *𝖯𝗎𝗋𝗀𝖾*

╭• /purge: Deletes messages upto replied message.

╭• /spurge: Deletes messages upto replied message without a success message.

╭• /del: Deletes a single message, used as a reply to message."""

__mod_name__ = "𝖯𝗎𝗋𝗀𝖾"
# <================================================ END =======================================================>
