import io
import logging
import os

import telebot

from wrapper.wrapper import Wrapper
from wrapper.files import InputVirtualFile

TOKEN = os.getenv("TG_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["help", "start"])
def handle_help(message):
    HELP_MSG = "Send nvs.csv and receive nvs.bin. Now it works only with 128k NVS partition size"
    bot.reply_to(message, HELP_MSG)


@bot.message_handler(
    func=lambda message: message.document.mime_type == "text/csv",
    content_types=["document"],
)
def handle_csv_document(message):
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    input = InputVirtualFile(downloaded_file.decode())
    size = 128 * 1024
    try:
        wrapper = Wrapper(input, size=size)
        output = wrapper.generate()
    except Exception as err:
        bot.reply_to(message, f"Something went wrong: {err}")
    else:
        bot.reply_to(message, f"nvs_partition_gen generate 0x{size:x}")
        bot.send_document(
            message.chat.id,
            telebot.types.InputFile(output),
            reply_to_message_id=message.message_id,
        )


@bot.message_handler(func=lambda _: True)
def other(message):
    OTHER_MSG = "Csv parsing from message is not supported yet"
    bot.reply_to(message, OTHER_MSG)


def main():
    logging.basicConfig(level=logging.INFO)
    bot.infinity_polling()


if __name__ == "__main__":
    main()
