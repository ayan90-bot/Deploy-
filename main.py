import os
from flask import Flask, request
import telebot
from pytube import YouTube
import tempfile

API_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(API_TOKEN)
server = Flask(__name__)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(message, "Hello! Please Send Video Link To Download Video.")

@bot.message_handler(func=lambda message: True)
def download_youtube_video(message):
    url = message.text.strip()
    try:
        # YouTube object banaiye
        yt = YouTube(url)
        stream = yt.streams.get_highest_resolution()

        # Temporary file mein video download karen
        temp_dir = tempfile.gettempdir()
        file_path = stream.download(output_path=temp_dir)

        # Video file Telegram chat me bhejein (20MB se choti files ke liye)
        if os.path.getsize(file_path) < 20 * 1024 * 1024:
            with open(file_path, 'rb') as video:
                bot.send_video(message.chat.id, video, caption=f"Yeh raha video: {yt.title}")
        else:
            bot.reply_to(message, "Sorry, video size bahut bada hai, upload nahi kar sakta.")

        # File delete karen after sending
        os.remove(file_path)

    except Exception as e:
        bot.reply_to(message, f"Error aaya: {str(e)}\nPlease sahi YouTube video link bhejein.")

# Flask routes for webhook
@server.route('/' + API_TOKEN, methods=['POST'])
def getMessage():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

@server.route("/")
def webhook_set():
    bot.remove_webhook()
    bot.set_webhook(url=os.environ.get("RENDER_EXTERNAL_URL") + "/" + API_TOKEN)
    return "Webhook set!", 200

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
