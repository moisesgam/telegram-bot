import os
import yt_dlp
import requests
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Token tomado desde variables de entorno (Render lo pide así)
TOKEN = os.getenv("TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 Envíame un link de YouTube y descargaré el audio con nombre y miniatura.\n"
        "⚠️ Solo usar con contenido permitido."
    )

async def recibir_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    await update.message.reply_text("🎧 Descargando audio… un momento.")

    # Obtener info del video
    try:
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)
            titulo = info.get("title", "audio")
            thumbnail_url = info.get("thumbnail")
    except Exception:
        await update.message.reply_text("❌ No pude obtener la información del video.")
        return

    # Crear nombre de archivo seguro
    nombre_seguro = "".join(c for c in titulo if c.isalnum() or c in " -_").rstrip()
    archivo_mp3 = f"{nombre_seguro}.mp3"
    archivo_jpg = "thumbnail.jpg"

    # Descargar miniatura
    try:
        r = requests.get(thumbnail_url)
        with open(archivo_jpg, "wb") as f:
            f.write(r.content)
    except:
        archivo_jpg = None

    # Descargar audio y convertir
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "temp_audio.%(ext)s",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Renombrar a nombre real
        if os.path.exists("temp_audio.mp3"):
            os.rename("temp_audio.mp3", archivo_mp3)

        # Preparar archivo para enviar
        audio_file = InputFile(open(archivo_mp3, "rb"), filename=archivo_mp3)

        # Enviar con miniatura si existe
        if archivo_jpg:
            thumb_file = InputFile(open(archivo_jpg, "rb"), filename="thumbnail.jpg")
            await update.message.reply_audio(
                audio=audio_file,
                title=titulo,
                thumbnail=thumb_file
            )
            os.remove(archivo_jpg)
        else:
            await update.message.reply_audio(
                audio=audio_file,
                title=titulo
            )

        os.remove(archivo_mp3)

    except Exception as e:
        await update.message.reply_text(f"❌ Error al procesar: {str(e)}")


def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_link))

    print("🎵 BOT CON MINIATURA + NOMBRE ACTIVADO")
    app.run_polling()

if __name__ == "__main__":
    main()
