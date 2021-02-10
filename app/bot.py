import logging
import os
import uuid

from dotenv import load_dotenv
from numpy import disp, load
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater

from app.ocr import extract_supplements

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Отправьте фото состава, чтобы извлечь ингредиенты!")


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Help!")


def photo(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_id = uuid.uuid4()
    photo_file.download(f"images/{photo_id}.jpg")
    logger.info("Photo of %s: %s", user.first_name, f"images/{photo_id}.jpg")

    update.message.reply_text("Извлекаю ингредиенты...")
    supplements = extract_supplements(f"images/{photo_id}.jpg")
    if supplements == []:
        update.message.reply_text("Ничего не обнаружено. Попробуйте другое изображение!")
    else:
        for sup in supplements:
            update.message.reply_text(f"{sup['full_title']} ({sup['category']}): {sup['effect']}")

        num_harmful = sum(x["is_harmful"] for x in supplements)
        if num_harmful > 0:
            update.message.reply_text(
                f"Обнаружены потенциально опасные ингредиенты ({num_harmful})!"
            )
        else:
            update.message.reply_text("Опасных ингредиентов не обнаружено!")
    os.remove(f"images/{photo_id}.jpg")


def main():
    TOKEN = os.getenv("TELEGRAM_TOKEN")

    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(MessageHandler(Filters.photo & ~Filters.command, photo))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
