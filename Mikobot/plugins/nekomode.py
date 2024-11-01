# SOURCE https://github.com/Team-ProjectCodeX
# CREATED BY https://t.me/O_okarma
# PROVIDED BY https://t.me/ProjectCodeX
# NEKOS

# <============================================== IMPORTS =========================================================>
import nekos
from telethon import events

from Database.mongodb.toggle_mongo import is_nekomode_on, nekomode_off, nekomode_on
from Mikobot import tbot
from Mikobot.state import state  # Import the state function

# <=======================================================================================================>

url_sfw = "https://api.waifu.pics/sfw/"

allowed_commands = [
    "waifu",
    "neko",
    "shinobu",
    "megumin",
    "bully",
    "cuddle",
    "cry",
    "hug",
    "awoo",
    "kiss",
    "lick",
    "pat",
    "smug",
    "bonk",
    "yeet",
    "blush",
    "smile",
    "spank",
    "wave",
    "highfive",
    "handhold",
    "nom",
    "bite",
    "glomp",
    "slap",
    "hTojiy",
    "wink",
    "poke",
    "dance",
    "cringe",
    "tickle",
]


# <================================================ FUNCTION =======================================================>
@tbot.on(events.NewMessage(pattern="/wallpaper"))
async def wallpaper(event):
    chat_id = event.chat_id
    nekomode_status = await is_nekomode_on(chat_id)
    if nekomode_status:
        target = "wallpaper"
        img_url = nekos.img(
            target
        )  # Replace nekos.img(target) with the correct function call
        await event.reply(file=img_url)


@tbot.on(events.NewMessage(pattern="/nekomode on"))
async def enable_nekomode(event):
    chat_id = event.chat_id
    await nekomode_on(chat_id)
    await event.reply("𝖭𝖾𝗄𝗈𝗆𝗈𝖽𝖾 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝖾𝗇𝖺𝖻𝗅𝖾𝖽.")


@tbot.on(events.NewMessage(pattern="/nekomode off"))
async def disable_nekomode(event):
    chat_id = event.chat_id
    await nekomode_off(chat_id)
    await event.reply("𝖭𝖾𝗄𝗈𝗆𝖺𝖽𝖾 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝖾𝗇𝖺𝖻𝗅𝖾𝖽")


@tbot.on(events.NewMessage(pattern=r"/(?:{})".format("|".join(allowed_commands))))
async def nekomode_commands(event):
    chat_id = event.chat_id
    nekomode_status = await is_nekomode_on(chat_id)
    if nekomode_status:
        target = event.raw_text[1:].lower()  # Remove the slash before the command
        if target in allowed_commands:
            url = f"{url_sfw}{target}"

            response = await state.get(url)
            result = response.json()
            animation_url = result["url"]

            # Send animation
            await event.respond(file=animation_url)


__help__ = """
╭• *𝖲𝖾𝗇𝖽𝗌 𝖿𝗎𝗇 𝗀𝗂𝖿/𝗂𝗆𝖺𝗀𝖾𝗌*

╭• /nekomode on : 𝖤𝗇𝖺𝖻𝗅𝖾𝗌 𝖿𝗎𝗇 𝗇𝖾𝗄𝗈𝗆𝗈𝖽𝖾.
╭• /nekomode off : 𝖣𝗂𝗌𝖺𝖻𝗅𝖾𝗌 𝖿𝗎𝗇 𝗇𝖾𝗄𝗈𝗆𝗈𝖽𝖾.

» /bully: sends random bully gifs.
» /neko: sends random neko gifs.
» /wallpaper: sends random wallpapers.
» /highfive: sends random highfive gifs.
» /tickle: sends random tickle GIFs.
» /wave: sends random wave GIFs.
» /smile: sends random smile GIFs.
» /feed: sends random feeding GIFs.
» /blush: sends random blush GIFs.
» /avatar: sends random avatar stickers.
» /waifu: sends random waifu stickers.
» /kiss: sends random kissing GIFs.
» /cuddle: sends random cuddle GIFs.
» /cry: sends random cry GIFs.
» /bonk: sends random cuddle GIFs.
» /smug: sends random smug GIFs.
» /slap: sends random slap GIFs.
» /hug: get hugged or hug a user.
» /pat: pats a user or get patted.
» /spank: sends a random spank gif.
» /dance: sends a random dance gif.
» /poke: sends a random poke gif.
» /wink: sends a random wink gif.
» /bite: sends random bite GIFs.
» /handhold: sends random handhold GIFs.
"""

__mod_name__ = "𝖭𝖾𝗄𝗈"
# <================================================ END =======================================================>
