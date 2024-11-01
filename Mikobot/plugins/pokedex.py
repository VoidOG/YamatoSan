# SOURCE https://github.com/Team-ProjectCodeX
# CREATED BY https://t.me/O_okarma
# API BY https://www.github.com/SOME-1HING
# PROVIDED BY https://t.me/ProjectCodeX

# <============================================== IMPORTS =========================================================>
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes

from Mikobot import function
from Mikobot.state import state

# <=======================================================================================================>


# <================================================ FUNCTIONS =====================================================>
async def get_pokemon_info(name_or_id):
    try:
        response = await state.get(
            f"https://sugoi-api.vercel.app/pokemon?name={name_or_id}"
        )
        if response.status_code == 200:
            return response.json()

        response = await state.get(
            f"https://sugoi-api.vercel.app/pokemon?id={name_or_id}"
        )
        if response.status_code == 200:
            return response.json()

    except Exception as e:
        print(f"𝖠𝗇 𝖾𝗋𝗋𝗈𝗋 𝗈𝖼𝖼𝗎𝗋𝖾𝖽: {str(e)}")

    return None


async def pokedex(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if context.args:
            name_or_id = context.args[0]
            pokemon_info = await get_pokemon_info(name_or_id)

            if pokemon_info:
                reply_message = (
                    f"╭• 𝖭𝖺𝗆𝖾: {pokemon_info['name']}\n"
                    f"╭• 𝖨𝖣: {pokemon_info['id']}\n"
                    f"╭• 𝖧𝖾𝗂𝗀𝗁𝗍: {pokemon_info['height']}\n"
                    f"╭• 𝖶𝖾𝗂𝗀𝗁𝗍: {pokemon_info['weight']}\n"
                )

                abilities = ", ".join(
                    ability["ability"]["name"] for ability in pokemon_info["abilities"]
                )
                reply_message += f"╭• 𝖠𝖻𝗂𝗅𝗂𝗍𝗂𝖾𝗌: {abilities}\n"

                types = ", ".join(
                    type_info["type"]["name"] for type_info in pokemon_info["types"]
                )
                reply_message += f"╭• 𝖳𝗒𝗉𝖾𝗌: {types}\n"

                image_url = f"https://img.pokemondb.net/artwork/large/{pokemon_info['name']}.jpg"

                # Create inline buttons
                keyboard = [
                    [
                        InlineKeyboardButton(text=" 𝖲𝗍𝖺𝗍𝗌", callback_data="stats"),
                        InlineKeyboardButton(text=" 𝖬𝗈𝗏𝖾𝗌", callback_data="moves"),
                    ]
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)

                await update.message.reply_photo(
                    photo=image_url,
                    caption=reply_message,
                    reply_markup=reply_markup,
                )
            else:
                await update.message.reply_text("𝖯𝗈𝗄𝖾𝗆𝗈𝗇 𝗇𝗈𝗍 𝖿𝗈𝗎𝗇𝖽.")
        else:
            await update.message.reply_text("𝖯𝗅𝖾𝖺𝗌𝖾 𝗀𝖺𝗏𝖾 𝖺 𝗉𝗈𝗄𝖾𝗆𝗈𝗇 𝗇𝖺𝗆𝖾 𝗈𝗋 𝖨𝖣")
    except Exception as e:
        await update.message.reply_text(f"𝖠𝗇 𝖾𝗋𝗋𝗈𝗋 𝗈𝖼𝖼𝗎𝗋𝖾𝖽: {str(e)}")


async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        name = query.message.caption.split("\n")[0].split(": ")[1]
        pokemon_info = await get_pokemon_info(name)

        if pokemon_info:
            stats = "\n".join(
                f"{stat['stat']['name'].upper()}: {stat['base_stat']}"
                for stat in pokemon_info["stats"]
            )
            stats_message = f"╭• 𝖲𝗍𝖺𝗍𝗌:\n{stats}\n"

            moves = ", ".join(
                move_info["move"]["name"] for move_info in pokemon_info["moves"]
            )
            moves_message = f"╭• 𝖬𝗈𝗏𝖾𝗌: {moves}"

            if query.data == "stats":
                await query.message.reply_text(stats_message)
            elif query.data == "moves":
                if len(moves_message) > 1000:
                    with open("moves.txt", "w") as file:
                        file.write(moves_message)
                    await query.message.reply_text(
                        "The moves exceed 1000 characters. Sending as a file.",
                        disable_web_page_preview=True,
                    )
                    await query.message.reply_document(document=open("moves.txt", "rb"))
                else:
                    await query.message.reply_text(moves_message)
        else:
            await query.message.reply_text("𝖯𝗈𝗄𝖾𝗆𝗈𝗇 𝗇𝗈𝗍 𝖿𝗈𝗎𝗇𝖽.")
    except Exception as e:
        await query.message.reply_text(f"𝖠𝗇 𝖾𝗋𝗋𝗈𝗋 𝗈𝖼𝖼𝗎𝗋𝗋𝖾𝖽: {str(e)}")


# <================================================ HANDLER =======================================================>
# Add the command and callback query handlers to the dispatcher
function(CommandHandler("pokedex", pokedex, block=False))
function(
    CallbackQueryHandler(callback_query_handler, pattern="^(stats|moves)$", block=False)
)

# <================================================ HANDLER =======================================================>
__help__ = """

╭• *𝖯𝗈𝗄𝖾𝗆𝗈𝗇 𝖲𝖾𝖺𝗋𝖼𝗁*

╭• *𝖢𝗈𝗆𝗆𝖺𝗇𝖽𝗌*:

╭•  /pokedex < Search > : 𝖦𝗂𝗏𝖾𝗌 𝗍𝗁𝖺𝗍 𝗉𝗈𝗄𝖾𝗆𝗈𝗇 𝗂𝗇𝖿𝗈.
"""

__mod_name__ = "𝖯𝗈𝗄𝖾𝖽𝖾𝗑"
# <================================================ END =======================================================>
