import logging
from threading import Thread

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler, CallbackQueryHandler

updater = Updater(token='580044798:AAErX88F0W8X9zryxtrIoayKGtTuo6zRJtA')

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

dispatcher = updater.dispatcher


def start(bot, update):
    keyboard = [[InlineKeyboardButton("지갑", callback_data='1'),
                 InlineKeyboardButton("거래 내역", callback_data='2')],

                [InlineKeyboardButton("Option 3", callback_data='3'),
                 InlineKeyboardButton("Opt 4", callback_data='4')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)


def echo(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="haha")


def alert_admin_run(msg):
    updater.bot.send_message(chat_id=592771270, text=msg)


def alert_admin(msg):
    t = Thread(target=alert_admin_run(msg))
    t.start()


def handle_incoming_message(bot, update):
    query = update.callback_query

    bot.edit_message_text(text="Selected option: {}".format(query.data),
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)


def chat_bot():
    return dispatcher.bot


def run():
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(CallbackQueryHandler(handle_incoming_message))

    updater.start_polling()
