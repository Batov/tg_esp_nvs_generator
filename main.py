import io
import logging
import os

import telebot

from nvs_partition_gen_wrapper import generate_nvs, InputFile, OutputFile

TOKEN = os.getenv("TG_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["help"])
def handle_help(message):
    HELP_MSG = "Send nvs.csv and receive nvs.bin"
    bot.reply_to(message, HELP_MSG)


@bot.message_handler(
    func=lambda message: message.document.mime_type == "text/csv",
    content_types=["document"],
)
def handle_csv_document(message):
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    try:
        output = generate_nvs(InputFile(downloaded_file.decode()))
    except Exception as err:
        bot.reply_to(message, f"Something went wrong: {err}")
    else:
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
