import os, asyncio, aiohttp
from dotenv import load_dotenv
from make_presentation import generate_presentation
from telegram import Update
from telegram.constants import ChatAction
from telegram.request import HTTPXRequest
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
COLAB_API_BASE = os.getenv("COLAB_API_BASE", "").rstrip("/")
HTTP_TIMEOUT = int(os.getenv("HTTP_TIMEOUT", "120"))

if not BOT_TOKEN or not COLAB_API_BASE:
    raise SystemExit("Нужно задать TELEGRAM_TOKEN и COLAB_API_BASE в .env")

# глобальные состояния
session: aiohttp.ClientSession | None = None
active_jobs: dict[int, bool] = {}  # user_id -> True/False

ASK_SLIDES, ASK_LANG = range(2)


async def ensure_session():
    global session
    if session is None or session.closed:
        session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=HTTP_TIMEOUT))
    return session


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Пришлите ссылку на аудио/видео или файл.\n⚠️ Только один запрос за раз!"
    )


async def _send_long_text(msg, title: str, text: str):
    if not text:
        await msg.reply_text(f"{title}: (пусто)")
        return
    if len(text) <= 3500:
        await msg.reply_text(f"**{title}:**\n{text}", parse_mode=None)
    else:
        from io import BytesIO

        bio = BytesIO(text.encode("utf-8"))
        bio.name = f"{title.lower().replace(' ','_')}.txt"
        await msg.reply_document(document=bio, filename=bio.name, caption=title)


async def _post_to_colab(source_url: str, session_id: str) -> dict:
    s = await ensure_session()
    url = f"{COLAB_API_BASE}/transcribe"
    form = aiohttp.FormData()
    form.add_field("source_url", source_url)
    form.add_field("do_summary", "true")
    form.add_field("session_id", session_id)
    async with s.post(url, data=form) as resp:
        if resp.status >= 400:
            body = await resp.text()
            raise RuntimeError(f"Colab {resp.status}: {body[:300]}")
        return await resp.json()


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg:
        return

    user_id = msg.from_user.id
    if active_jobs.get(user_id, False):
        await msg.reply_text("⏳ Подождите, предыдущая задача ещё выполняется!")
        return
    active_jobs[user_id] = True

    await msg.reply_chat_action(ChatAction.TYPING)

    try:
        session_id = f"{user_id}_{msg.id}"

        if msg.text and msg.text.strip().startswith(("http://", "https://")):
            src = msg.text.strip()
            await msg.reply_text("➡️ Отправляю на сервер…")
            res = await _post_to_colab(src, session_id)
        else:
            file_obj = msg.audio or msg.voice or msg.video or msg.document
            if not file_obj:
                await msg.reply_text("Пришлите ссылку или файл (audio/video/voice/document).")
                return
            tg_file = await file_obj.get_file()

            # формируем прямую ссылку на файл
            if tg_file.file_path.startswith("http"):
                direct_url = tg_file.file_path
            else:
                direct_url = f"https://api.telegram.org/file/bot{context.bot.token}/{tg_file.file_path.lstrip('/')}"

            await msg.reply_text("➡️ Отправляю файл на сервер…")
            res = await _post_to_colab(direct_url, session_id)

        # После получения транскрипта и резюме
        text = res.get("text") or ""
        summary = res.get("summary") or ""

        await _send_long_text(msg, "Транскрипт", text)
        await _send_long_text(msg, "Резюме", summary)

        # сохраняем данные
        context.user_data["text"] = text
        context.user_data["summary"] = summary

        # спрашиваем количество слайдов
        await msg.reply_text("Сколько слайдов сделать? (по умолчанию 5)")
        return ASK_SLIDES

    except asyncio.TimeoutError:
        await msg.reply_text("⏱ Сервер не ответил вовремя. Попробуйте позже.")
        active_jobs[user_id] = False
        return ConversationHandler.END
    except Exception as e:
        await msg.reply_text(f"💥 Ошибка: {e}")
        active_jobs[user_id] = False
        return ConversationHandler.END


async def ask_slides(update: Update, context: ContextTypes.DEFAULT_TYPE):
    slides = update.message.text.strip()
    try:
        n_slides = int(slides)
    except:
        n_slides = 5
    context.user_data["slides"] = n_slides

    await update.message.reply_text("На каком языке презентация? (например: Russian, English)")
    return ASK_LANG


async def ask_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = update.message.text.strip()
    context.user_data["language"] = lang or "Russian"

    slides = context.user_data.get("slides", 5)
    language = context.user_data.get("language", "Russian")
    text = context.user_data.get("text", "")
    summary = context.user_data.get("summary", "")

    await update.message.reply_text(
        f"🚀 Приступаем к созданию презентации!\n\n"
        f"📊 Слайдов: {slides}\n"
        f"🌍 Язык: {language}"
    )

    try:
        content = f"Транскрипт:\n{text}\n\nРезюме:\n{summary}"
        ppt = await generate_presentation(content, n_slides=slides, language=language)

        await update.message.reply_text(
            f"🎉 Презентация готова!\n\n"
            f"📥 Скачать PPTX: {ppt['path']}\n"
            f"✏️ Редактировать онлайн: {ppt['edit_path']}"
        )
    except Exception as e:
        await update.message.reply_text(f"💥 Ошибка при генерации презентации: {e}")

    user_id = update.message.from_user.id
    active_jobs[user_id] = False
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚫 Отменено")
    return ConversationHandler.END


async def on_shutdown(app):
    global session
    if session and not session.closed:
        await session.close()


def main():
    request = HTTPXRequest(connect_timeout=20.0, read_timeout=180.0)
    app = ApplicationBuilder().token(BOT_TOKEN).request(request).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.ALL & ~filters.COMMAND, handle)],
        states={
            ASK_SLIDES: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_slides)],
            ASK_LANG: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_language)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

    print("Bot is running…")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
