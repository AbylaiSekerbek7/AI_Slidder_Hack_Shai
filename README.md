# 🎥 AI Slidder – ИИ-интерпретатор креативного контента

## 📌 Описание
**AI Slidder** — это интеллектуальный агент, который:
- Принимает **аудио/видео/ссылку** от пользователя через Telegram-бота.
- Выполняет **транскрибацию речи в текст** с помощью [Whisper](https://github.com/openai/whisper).
- Создает **резюме (summary)** на основе текста (поддержка русского и английского).
- Автоматически генерирует **красивую презентацию (PPTX)** на основе транскрипта и резюме с использованием **Presenton API** или локальной версии.

## ⚙️ Стек технологий
- **Python 3.11**
- [Telegram Bot API](https://core.telegram.org/bots/api)  
- [FastAPI](https://fastapi.tiangolo.com/) + **ngrok** для локального хостинга  
- [OpenAI Whisper](https://github.com/openai/whisper) (GPU ускорение на Colab/Kaggle/Docker)  
- [Transformers (HuggingFace)](https://huggingface.co/docs/transformers) для суммаризации текста  
- [Presenton](https://presenton.ai) – генерация презентаций  

## 🚀 Возможности
- Поддержка **аудио и видео файлов** (mp3, mp4, wav и др.)
- Работа по ссылке (YouTube, Telegram file link и т.д.)
- Автоматическое **распознавание языка транскрипта**
- Возможность выбрать:
  - Количество слайдов
  - Язык презентации
- Выдача результата в виде:
  - `Транскрипта`
  - `Резюме`
  - `Скачиваемой презентации PPTX`

## 🖼️ Демонстрация
📌 Интерфейс Telegram-бота:  
![alt text](image.png)

📌 Пример слайдов презентации:  
![alt text](image-1.png)
![alt text](image-2.png)
![alt text](image-3.png)

## 🔧 Установка и запуск
1. Клонируем репозиторий:
   ```bash
   git clone https://github.com/AbylaiSekerbek7/AI_Slidder_Hack_Shai
   cd bot

2. Создаем файл .env и добавляем туда ключи:
    ```bash
    TELEGRAM_TOKEN=ваш_токен_бота
    COLAB_API_BASE=ваш_сервер_Colab/ngrok
    PRESENTON_API_KEY=ваш_api_ключ

3. Запускаем бота:
    ```bash
    python bot.py

🏗️ Архитектура
Telegram Bot  →  FastAPI (ngrok)  →  Whisper (GPU)  →  Summarizer  →  Presenton API

📈 Потенциал и интеграции

Интеграция с корпоративными API (Zoom, CRM, ERP)

Возможность добавления next-best-action подсказок

Масштабируемость через Docker и Kubernetes

👨‍💻 Авторы

Команда AI Slidder Hack Team 🚀

Abylaikhan Sekerbek
Amirlan Sarsenov
