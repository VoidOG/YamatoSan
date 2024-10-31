# <============================================== IMPORTS =========================================================>
from asyncio import sleep

from telethon import events
from telethon.errors import ChatAdminRequiredError, UserAdminInvalidError
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChannelParticipantsAdmins, ChatBannedRights

from Mikobot import SUPPORT_STAFF, tbot

# <=======================================================================================================>

BANNED_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True,
)

UNBAN_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=None,
    send_media=None,
    send_stickers=None,
    send_gifs=None,
    send_games=None,
    send_inline=None,
    embed_links=None,
)


# <==================================================== FUNCTION ===================================================>
async def is_administrator(user_id: int, message):
    admin = False
    async for user in tbot.iter_participants(
        message.chat_id, filter=ChannelParticipantsAdmins
    ):
        if user_id == user.id or user_id in SUPPORT_STAFF:
            admin = True
            break
    return admin


@tbot.on(events.NewMessage(pattern="^[!/]zombies ?(.*)"))
async def rm_deletedacc(show):
    con = show.pattern_match.group(1).lower()
    del_u = 0
    del_status = "Group is clean, 0 deleted accounts found."
    if con != "clean":
        kontol = await show.reply("`Searching for deleted account𝗌...`")
        async for user in show.client.iter_participants(show.chat_id):
            if user.deleted:
                del_u += 1
                await sleep(1)
        if del_u > 0:
            del_status = (
                f"Searching... `{del_u}`deleted account(s) found ,"
                "\nclean it with command `/zombies clean`"
            )
        return await kontol.edit(del_status)
    chat = await show.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        return await show.reply("Sorry, you're not an admin!")
    ok = await show.reply("`Banning deleted accounts...`")
    del_u = 0
    del_a = 0
    async for user in tbot.iter_participants(show.chat_id):
        if user.deleted:
            try:
                await show.client(
                    EditBannedRequest(show.chat_id, user.id, BANNED_RIGHTS)
                )
            except ChatAdminRequiredError:
                return await show.edit("I don't have ban rights in this group")
            except UserAdminInvalidError:
                del_u -= 1
                del_a += 1
            await tbot(EditBannedRequest(show.chat_id, user.id, UNBAN_RIGHTS))
            del_u += 1
    if del_u > 0:
        del_status = f"𝖢𝗅𝖾𝖺𝗇𝖾𝖽 `{del_u}` 𝗓𝗈𝗆𝖻𝗂𝖾𝗌"
    if del_a > 0:
        del_status = (
            f"Zombies `{del_u}` 𝗓𝗈𝗆𝖻𝗂𝖾𝗌 " f"\n`{del_a}` 𝖺𝖽𝗆𝗂𝗇 𝗓𝗈𝗆𝖻𝗂𝖾𝗌 𝖺𝗋𝖾 𝗇𝗈𝗍 𝖽𝖾𝗅𝖾𝗍𝖾𝖽."
        )
    await ok.edit(del_status)


# <=======================================================================================================>


# <==================================================== HELP ===================================================>
__help__ = """
╭• *𝖱𝖾𝗆𝗈𝗏𝖾 𝖣𝖾𝗅𝖾𝗍𝖾𝖽 𝖠𝖼𝖼𝗈𝗎𝗇𝗍𝗌*:

» /zombies: Starts searching for deleted accounts in the group.

» /zombies clean: Removes the deleted accounts from the group.
"""
__mod_name__ = "𝖹𝗈𝗆𝖻𝗂𝖾𝗌"
# <==================================================== END ===================================================>
