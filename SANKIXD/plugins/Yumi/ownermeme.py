from pyrogram import Client, filters
import requests
from SANKIXD import app
import time
from threading import Thread

# Owner ID (replace with your actual Telegram user ID)
OWNER_ID = 7548678061  # Replace with your Telegram user ID

# Channel username
CHANNEL_USERNAME = "@SANKI_MEMES"  # Replace with your channel username

# Global variables for controlling auto-upload
auto_upload = False
uploaded_memes = set()  # To track already uploaded memes

def fetch_meme():
    """Fetch a meme from the API."""
    api_url = "https://meme-api.com/gimme"
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            meme_url = data.get("url")
            title = data.get("title")
            return meme_url, title
        else:
            return None, None
    except Exception as e:
        print(f"Error fetching meme: {e}")
        return None, None

def auto_upload_memes():
    """Automatically upload memes to the channel every hour."""
    global auto_upload
    while auto_upload:
        meme_url, title = fetch_meme()
        if meme_url and meme_url not in uploaded_memes:
            try:
                # Send meme to the channel
                app.send_photo(
                    chat_id=CHANNEL_USERNAME,
                    photo=meme_url,
                    caption=f"{title}\n\nShared via @{app.get_me().username}"
                )
                uploaded_memes.add(meme_url)  # Mark meme as uploaded
                print(f"Meme uploaded: {meme_url}")
            except Exception as e:
                print(f"Error uploading meme: {e}")
        else:
            print("No new meme found or duplicate meme.")
        time.sleep(3600)  # Wait for 1 hour

# Command: /meme on
@app.on_message(filters.command("memes") & filters.user(OWNER_ID))
def meme_control(client, message):
    global auto_upload

    # Parse the argument (on/off)
    command_arg = message.text.split(maxsplit=1)[1].lower() if len(message.text.split()) > 1 else None

    if command_arg == "on":
        if not auto_upload:
            auto_upload = True
            message.reply_text("Automatic meme uploading started!")
            # Start the auto-uploading thread
            Thread(target=auto_upload_memes).start()
        else:
            message.reply_text("Automatic meme uploading is already running.")
    elif command_arg == "off":
        if auto_upload:
            auto_upload = False
            message.reply_text("Automatic meme uploading stopped!")
        else:
            message.reply_text("Automatic meme uploading is already stopped.")
    else:
        message.reply_text("Usage: /memes on|off")

# Command: /meme (manual meme fetch)
@app.on_message(filters.command("meme") & ~filters.user(OWNER_ID))
def meme_command(client, message):
    # API endpoint for random memes
    meme_url, title = fetch_meme()

    if meme_url:
        caption = f"{title}\n\nRequest by {message.from_user.mention}\nBot username: @{app.get_me().username}"
        try:
            # Send the meme to the user
            message.reply_photo(
                photo=meme_url,
                caption=caption
            )
        except Exception as e:
            print(f"Error sending meme: {e}")
            message.reply_text("Sorry, I couldn't fetch a meme at the moment.")
    else:
        message.reply_text("Sorry, I couldn't fetch a meme at the moment.")
