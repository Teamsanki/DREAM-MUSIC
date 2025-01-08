from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import pymongo
from SANKIXD import app
import asyncio
from config import BOT_TOKEN, API_ID, API_HASH, MONGO_DB_URI, BIRTHDAY_PHOTO

# Initialize the bot
app = Client("birthday_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

# MongoDB client setup
client = pymongo.MongoClient(MONGO_DB_URI)
db = client["birthday_db"]  # Database name
users_collection = db["users"]  # Collection to store users' birthdays

# Function to send birthday message
async def send_birthday_message(user_id, username, user_bday):
    birthday_message = (
        f"🎉🌟 **Happy Birthday to {username}!** 🌟🎉\n\n"
        f"🎂 **It's your special day!** 🎂\n"
        f"💖 **We wish you a fantastic year ahead!** 💖\n\n"
        f"🎈 May happiness, success, and love always brighten your way. 🎈\n"
        f"🎁 **Enjoy every moment!** 🥳"
    )
    
    # Inline button for user's profile
    buttons = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🎉 Wish {username} 🎉", url=f"tg://user?id={user_id}")]]
    )

    # Send the birthday message to user and in the group (if bot is part of a group)
    async for dialog in app.get_dialogs():
        try:
            if dialog.chat.type in ["group", "supergroup"]:
                await app.send_photo(
                    chat_id=dialog.chat.id,
                    photo=BIRTHDAY_PHOTO,
                    caption=birthday_message,
                    reply_markup=buttons
                )
        except Exception as e:
            print(f"Failed to send message to {dialog.chat.title}: {e}")
    
    # Send direct message (DM) to the user
    await app.send_photo(
        chat_id=user_id,
        photo=BIRTHDAY_PHOTO,
        caption=birthday_message,
        reply_markup=buttons
    )


# Command to edit user's birthday
@app.on_message(filters.command("editbdy", prefixes="/"))
async def edit_birthday(_, message):
    user_id = message.from_user.id
    user = users_collection.find_one({"user_id": user_id})
    
    if not user:
        await message.reply("You haven't set your birthday yet. Please use /setbdy to set it first.")
        return
    
    # Show current birthday date
    current_bday = user.get("birthday", "not set")
    await message.reply(f"Your current birthday is set as {current_bday}.\n"
                        "To update, please enter the new birthday in the format DD-MM-YYYY.")
    
    # Ask for new date input
    @app.on_message(filters.regex(r"^\d{2}-\d{2}-\d{4}$"))
    async def update_birthday(_, message):
        new_bday = message.text.strip()
        if not new_bday:
            await message.reply("Please enter a valid date in the format DD-MM-YYYY.")
            return
        
        # Update in MongoDB
        users_collection.update_one(
            {"user_id": user_id},
            {"$set": {"birthday": new_bday}},
        )

        # Loading animation to show the user the process is ongoing
        loading_message = await message.reply("Updating your birthday...")

        # Show loading animation (use dashes as loading effect)
        loading_effects = ["-", "--", "---", "----", "-----", "------", "-------"]
        for effect in loading_effects:
            await asyncio.sleep(1)
            await loading_message.edit_text(f"Updating your birthday {effect}")
        
        # Send confirmation message
        await message.reply(f"Your birthday has been updated to {new_bday}. 🎉")
        await send_birthday_message(user_id, user['username'], new_bday)

