import os

import unidecode
from PIL import Image, ImageChops, ImageDraw, ImageFont
from pyrogram import filters
from pyrogram.enums import ParseMode

from Mikobot import DEMONS, DEV_USERS, DRAGONS, OWNER_ID, TIGERS, WOLVES, app


async def circle(pfp, size=(900, 900)):
    pfp = pfp.resize(size, Image.ANTIALIAS).convert("RGBA")
    bigsize = (pfp.size[0] * 3, pfp.size[1] * 3)
    mask = Image.new("L", bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(pfp.size, Image.ANTIALIAS)
    mask = ImageChops.darker(mask, pfp.split()[-1])
    pfp.putalpha(mask)
    return pfp


async def download_and_process_pfp(user):
    try:
        pic = await app.download_media(
            user.photo.big_file_id, file_name=f"pp{user.id}.png"
        )
        if pic:
            pfp = Image.open(pic).convert("RGBA")
            return await circle(pfp, size=(900, 900))
    except Exception as e:
        print(e)
    finally:
        if "pic" in locals() and pic:
            os.remove(pic)
    return None


async def userinfopic(
    user,
    user_x,
    user_y,
    user_id_x,
    user_id_y,
    pfp_x_offset=0,
    pfp_y_offset=0,
    pfp_size=(1218, 1385),
):
    user_name = unidecode.unidecode(user.first_name)

    # Load the background image
    background = Image.open("Extra/user.jpg")
    background = background.resize(
        (background.size[0], background.size[1]), Image.ANTIALIAS
    )

    draw = ImageDraw.Draw(background)
    font = ImageFont.truetype("Extra/default.ttf", 100)

    try:
        pfp = await download_and_process_pfp(user)
        if pfp:
            # Adjust pfp_x and pfp_y with the offsets
            pfp_x = 927 + pfp_x_offset
            pfp_y = (background.size[1] - pfp.size[1]) // 2 - 290 + pfp_y_offset

            # Increase the size of the pfp circle
            pfp = await circle(pfp, size=pfp_size)
            background.paste(pfp, (pfp_x, pfp_y), pfp)

        user_text_width, user_text_height = draw.textsize(user_name, font=font)
        user_id_text_width, user_id_text_height = draw.textsize(str(user.id), font=font)

        draw.text((user_x, user_y), user_name, font=font, fill="white")
        draw.text((user_id_x, user_id_y), str(user.id), font=font, fill="white")

        userinfo = f"downloads/userinfo_{user.id}.png"
        background.save(userinfo)

    except Exception as e:
        print(e)
        userinfo = None

    return userinfo


# Command handler for /userinfo
@app.on_message(filters.command("uinfo"))
async def userinfo_command(client, message):
    user = message.from_user
    user_x, user_y = 1035, 2885
    user_id_x, user_id_y = 1035, 2755

    try:
        # Send a message indicating that user information is being processed
        processing_message = await message.reply("𝖯𝗋𝗈𝖼𝖾𝗌𝗌𝗂𝗇𝗀 𝗎𝗌𝖾𝗋 𝗂𝗇𝖿𝗈𝗋𝗆𝖺𝗍𝗂𝗈𝗇...")

        # Generate user info image
        image_path = await userinfopic(user, user_x, user_y, user_id_x, user_id_y)

        # Delete the processing message
        await processing_message.delete()

        if image_path:
            # Initialize the caption with basic information
            caption = (
                f"「 **𝖠𝖼𝖼𝗈𝗋𝖽𝗂𝗇𝗀 𝗍𝗈 𝖸𝖺𝗆𝖺𝗍𝗈'𝗌 𝖠𝗇𝖺𝗅𝗈𝗀𝗒, 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋𝗂𝗇𝖿𝗈 𝗂𝗌...** : 」\n\n"
                f"╭•  𝖨𝖣: {user.id}\n"
                f"╭•  𝖥𝗂𝗋𝗌𝗍 𝖭𝖺𝗆𝖾: {user.first_name}\n"
                f"╭•  𝖫𝖺𝗌𝗍 𝖭𝖺𝗆𝖾: {user.last_name}\n"
                f"╭•  𝖴𝗌𝖾𝗋𝗇𝖺𝗆𝖾: {user.username}\n"
                f" ╭• 𝖴𝗌𝖾𝗋𝗅𝗂𝗇𝗄: [𝖫𝗂𝗇𝗄](tg://openmessage?user_id={user.id})\n"
            )

            # Check if the user's ID matches one of the predefined ranks
            if user.id == OWNER_ID:
                caption += "\n\n〄 𝖳𝗁𝖾 𝖽𝗂𝗌𝖺𝗌𝗍𝖾𝗋 𝗅𝖾𝗏𝖾𝗅 𝗈𝖿 𝗍𝗁𝗂𝗌 𝗎𝗌𝖾𝗋 𝗂𝗌 **Owner**.\n"
            elif user.id in DEV_USERS:
                caption += "\n\n〄 𝖳𝗁𝗂𝗌 𝗎𝗌𝖾𝗋 𝗂𝗌 𝖺 𝗆𝖾𝗆𝖻𝖾𝗋 𝗈𝖿 **𝖣𝖾𝗏𝖾𝗅𝗈𝗉𝖾𝗋**.\n"
            elif user.id in DRAGONS:
                caption += "\n\n〄 𝖳𝗁𝖾 𝖽𝗂𝗌𝖺𝗌𝗍𝖾𝗋 𝗅𝖾𝗏𝖾𝗅 𝗈𝖿 𝗍𝗁𝗂𝗌 𝗎𝗌𝖾𝗋 𝗂𝗌 **𝖲𝗎𝖽𝗈**.\n"
            elif user.id in DEMONS:
                caption += "\n\n〄 𝖳𝗁𝖾 𝖽𝗂𝗌𝖺𝗌𝗍𝖾𝗋 𝗅𝖾𝗏𝖾𝗅 𝗈𝖿 𝗍𝗁𝗂𝗌 𝗎𝗌𝖾𝗋 𝗂𝗌 **𝖣𝖾𝗆𝗈𝗇**.\n"
            elif user.id in TIGERS:
                caption += "\n\n〄 𝖳𝗁𝖾 𝖽𝗂𝗌𝖺𝗌𝗍𝖾𝗋 𝗅𝖾𝗏𝖾𝗅 𝗈𝖿 𝗍𝗁𝗂𝗌 𝗎𝗌𝖾𝗋 𝗂𝗌 **𝖳𝗂𝗀𝖾𝗋**.\n"
            elif user.id in WOLVES:
                caption += "\n\n〄 𝖳𝗁𝖾 𝖽𝗂𝗌𝖺𝗌𝗍𝖾𝗋 𝗅𝖾𝗏𝖾𝗅 𝗈𝖿 𝗍𝗁𝗂𝗌 𝗎𝗌𝖾𝗋 𝗂𝗌 **𝖶𝗈𝗅𝖿**.\n"

            # Add the RANK line only if the user's ID matches one of the predefined ranks
            if (
                user.id == OWNER_ID
                or user.id in DEV_USERS
                or user.id in DRAGONS
                or user.id in DEMONS
                or user.id in TIGERS
                or user.id in WOLVES
            ):
                caption += "\n\n〄 𝖱𝖺𝗇𝗄: "

                if user.id == OWNER_ID:
                    caption += "**𝖢𝗋𝖾𝖺𝗍𝗈𝗋**"
                elif user.id in DEV_USERS:
                    caption += "**𝖣𝖾𝗏𝖾𝗅𝗈𝗉𝖾𝗋**"
                elif user.id in DRAGONS:
                    caption += "**𝖣𝗋𝖺𝗀𝗈𝗇**"
                elif user.id in DEMONS:
                    caption += "**𝖣𝖾𝗆𝗈𝗇**"
                elif user.id in TIGERS:
                    caption += "**𝖳𝗂𝗀𝖾𝗋**"
                elif user.id in WOLVES:
                    caption += "**𝖶𝗈𝗅𝖿**"

                caption += "\n"

            await message.reply_photo(
                photo=image_path, caption=caption, parse_mode=ParseMode.MARKDOWN
            )
            os.remove(image_path)

    except Exception as e:
        print(e)
