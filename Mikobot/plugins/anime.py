import html
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler
from Mikobot import dispatcher
from Mikobot.plugins.log_channel import loggable

DEFAULT_SERVICE_URLS = ["https://example.com/service1", "https://example.com/service2"]
LANGUAGES = ["English", "Japanese", "French"]

@loggable
async def anime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Replace with your image URL and caption
    image_url = "https://i.ibb.co/VJcX8Qk/file-1039.jpg"  # URL of the image
    caption_text = "Reserved for something special!"  # Caption text for the image

    # Sending the image with the caption
    await update.message.reply_photo(
        photo=image_url,
        caption=caption_text,
        parse_mode="HTML"
    )

# Handler for the /anime command
ANIME_HANDLER = CommandHandler("anime", anime)

# Add the handler to the dispatcher
dispatcher.add_handler(ANIME_HANDLER)

__command_list__ = ["anime"]
__handlers__ = [ANIME_HANDLER]

# <================================================= HELP ======================================================>
__help__ = """
𝗂𝗇𝗉𝗎𝗍
"""

__mod_name__ = "𝖠𝗇𝗂𝗆𝖾"
# <================================================== END =====================================================>
