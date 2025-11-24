import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import yt_dlp

TOKEN = os.getenv("TOKEN")

async def download_audio(url: str):
    ydl_opts = {
        "format": "bestaudio/best",
        "cookiefile": "cookies.txt",  # ← cookies activadas
        "outtmpl": "%(title)s.%(ext)s",
        "quiet": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3")
        title = info.get("title", "audio")
        thumbnail = info.get("thumbnail", None)
        return filename, title, thumbnail

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    await update.message.reply_text("🎧 Descargando audio, espera un momento…")

    try:
        filename, title, thumbnail = await download_audio(url)

        with open(filename, "rb") as f:
            await update.message.reply_audio(
                audio=f,
                title=title,
                thumbnail=thumbnail
            )

        os.remove(filename)

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
