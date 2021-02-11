import logging
import os
import uuid
from typing import Dict, List

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


def prepare_entry_text(supplement: Dict) -> str:
    return f"{supplement['full_title']} ({supplement['category']}): {supplement['effect']}"


def process_reply(update: Update, supplements: List[dict]) -> None:
    if supplements == []:
        update.message.reply_text("Ничего не обнаружено. Попробуйте другое изображение!")
    else:
        for sup in supplements:
            update.message.reply_text(prepare_entry_text(sup))


def prepare_summary_message(num_harmful: int) -> str:
    if num_harmful > 0:
        return f"Обнаружены потенциально опасные ингредиенты ({num_harmful})!"
    return "Опасных ингредиентов не обнаружено!"


def photo(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_id = uuid.uuid4()
    photo_file.download(f"images/{photo_id}.jpg")
    logger.info("Photo of %s: %s", user.first_name, f"images/{photo_id}.jpg")

    update.message.reply_text("Извлекаю ингредиенты...")
    supplements = extract_supplements(f"images/{photo_id}.jpg")
    process_reply(update, supplements)

    num_harmful = sum(x["is_harmful"] for x in supplements)
    update.message.reply_text(prepare_summary_message(num_harmful))
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
