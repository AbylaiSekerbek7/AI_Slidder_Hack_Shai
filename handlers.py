# bot/handlers.py
from telegram import Update
from telegram.ext import ContextTypes
from .utils import process_video
from pathlib import Path

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Пришли мне видео или ссылку на видео, и я сделаю презентацию."
    )

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Начинаю обработку видео... Это может занять несколько минут.")

    # Получаем файл
    video_file = await update.message.video.get_file()
    video_path = Path("output") / video_file.file_id
    await video_file.download_to_drive(str(video_path))

    # Генерируем презентацию
    pptx_path = process_video(str(video_path))

    # Отправляем пользователю
    await update.message.reply_document(document=open(pptx_path, "rb"))
