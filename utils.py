# bot/utils.py
import os
from pathlib import Path
from modules.video_download import download_video
from modules.audio_extract import extract_audio
from modules.stt import transcribe_audio
from modules.summarize import summarize_text
from modules.make_presentation import create_presentation  # твоя функция, которую нужно вынести как функцию

OUTPUT_DIR = Path("output")

def process_video(url_or_file):
    """
    Принимает ссылку на видео или путь к файлу.
    Возвращает путь к готовой презентации.
    """
    # 1. Скачиваем видео
    video_path = download_video(url_or_file, OUTPUT_DIR)

    # 2. Извлекаем аудио
    audio_path = extract_audio(video_path, OUTPUT_DIR)

    # 3. Расшифровка аудио
    transcript = transcribe_audio(audio_path)

    # 4. Суммаризация
    summary = summarize_text(transcript)

    # 5. Создание презентации
    pptx_path = create_presentation(summary, OUTPUT_DIR)

    return pptx_path
