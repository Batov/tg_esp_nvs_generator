import telebot
import logging
import os
from nvs_partition_gen_wrapper import generate_nvs
import io

TOKEN = os.getenv("TG_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

RESPONCE_BIN_FILE_NAME = "nvs.bin"


class NamedBytesIO(io.BytesIO):
    name = RESPONCE_BIN_FILE_NAME


@bot.message_handler(commands=["help"])
def handle_help(message):
    HELP_MSG = "I am help message"
    bot.reply_to(message, HELP_MSG)


@bot.message_handler(
    func=lambda message: message.document.mime_type == "text/csv",
    content_types=["document"],
)
def handle_csv_document(message):
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    output = generate_nvs(downloaded_file)
    virtual_output_file = NamedBytesIO(output)
    bot.send_document(message.chat.id, telebot.types.InputFile(virtual_output_file))


@bot.message_handler(func=lambda _: True)
def other(message):
    OTHER_MSG = "Is not supported yet"
    bot.reply_to(message, OTHER_MSG)


def main():
    logging.basicConfig(level=logging.INFO)
    bot.infinity_polling()


if __name__ == "__main__":
    main()
