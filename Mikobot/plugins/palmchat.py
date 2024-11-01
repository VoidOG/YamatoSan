from pyrogram import filters

from Mikobot import app
from Mikobot.state import state

# Configuration - The PALM API URL
PALM_API_URL = "https://lexica.qewertyy.dev/models"
MODEL_ID = 1  # Modify this if you have a specific model ID to use


# Function to call the PALM API and get the response
async def get_palm_response(api_params):
    try:
        response = await state.post(PALM_API_URL, params=api_params)
        if response.status_code == 200:
            data = response.json()
            return data.get(
                "content", "𝖤𝗋𝗋𝗈𝗋: 𝖤𝗆𝗉𝗍𝗒 𝗋𝖾𝗌𝗉𝗈𝗇𝗌𝖾 𝗋𝖾𝖼𝖾𝗂𝗏𝖾𝖽 𝖿𝗋𝗈𝗆 𝗉𝖺𝗅𝗆𝖠𝖯𝖨."
            )
        else:
            return f"𝖤𝗋𝗋𝗈𝗋: 𝖱𝖾𝗊𝗎𝖾𝗌𝗍 𝖿𝖺𝗂𝗅𝖾𝖽 𝗐𝗂𝗍𝗁 𝗌𝗍𝖺𝗍𝗎𝗌 𝖼𝗈𝖽𝖾 {response.status_code}."
    except fetch.RequestError as e:
        return f"Error: An error occurred while calling the PALM API. {e}"


# Command handler for /palm
@app.on_message(filters.text)
async def palm_chatbot(client, message):
    if not message.text.startswith("𝖸𝖺𝗆𝖺𝗍𝗈"):
        return
        # your code here
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("𝖦𝗂𝗏𝖾 𝗆𝖾 𝖺 𝗊𝗎𝖾𝗋𝗒 𝗍𝗈 𝗌𝖾𝖺𝗋𝖼𝗁")
        return

    input_text = args[1]

    # Send the "giving results" message first
    result_msg = await message.reply("🔍")

    # Call the PALM API to get the chatbot response asynchronously
    api_params = {"model_id": MODEL_ID, "prompt": input_text}
    api_response = await get_palm_response(api_params)

    # Delete the "giving results" message
    await result_msg.delete()

    # Send the chatbot response to the user
    await message.reply(api_response)


__help__ = """
╭• *𝖶𝗋𝗂𝗍𝖾 𝖸𝖺𝗆𝖺𝗍𝗈 𝗐𝗂𝗍𝗁 𝖺𝗇𝗒 𝗌𝖾𝗇𝗍𝖾𝗇𝖼𝖾, 𝗂𝗍 𝗐𝗂𝗅 𝗐𝗈𝗋𝗄 𝖺𝗌 𝖼𝗁𝖺𝗍𝖻𝗈𝗍*

╭• *𝖤𝗑𝖺𝗆𝗉𝗅𝖾*: 𝖸𝖺𝗆𝖺𝗍𝗈 𝖺𝗋𝖾 𝗒𝗈𝗎 𝖺 𝖻𝗈𝗍?
"""

__mod_name__ = "𝖢𝗁𝖺𝗍𝖻𝗈𝗍"
