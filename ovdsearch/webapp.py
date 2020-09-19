import telebot
import json
import logging
from copy import deepcopy
from collections import defaultdict

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
)

from .db import Database

logging.basicConfig(
    filename="bot.log",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
)
logger = logging.getLogger(__name__)

with open("../keys", "r") as f:
    keys = json.load(f)

# TODO databases

REQUEST_KWARGS = {
    "proxy_url": keys["PROXY_URL"],
    "urllib3_proxy_kwargs": {
        "username": keys["PROXY_USER"],
        "password": keys["PROXY_PASSWORD"],
    },
}


def db_get_task(user_id):
    prisoner_id = 1
    prisoner_name = "Владимир Путин"
    ovd_id = 10
    ovd_name = "ОВД по Московскому Кремлю"
    ovd_address = "Москва, Кремль"
    ovd_phones = ["+79123456780", "+79123456781"]
    return True, prisoner_id, prisoner_name, ovd_id, ovd_name, ovd_address, ovd_phones


def db_process_finding(prisoner_id, ovd_id):
    pass


def db_process_not_finding(prisoner_id, ovd_id):
    pass


def db_get_prisoner_searchers(prisoner_id):
    return []


# flow:
# start -> add_prisoner
# add_prisoner -> ?
class Bot:
    def __init__(self, token, db, request_kwargs=None):
        self.db: Database = db
        # словарь с состоянием бота для каждого из пользователей
        self.current_actions = {}
        logging.info("New session started!")

        updater = Updater(token=token, use_context=True, request_kwargs=request_kwargs)
        self.updater = updater
        dispatcher = updater.dispatcher

        dispatcher.add_handler(CommandHandler("start", self.start))
        dispatcher.add_handler(CallbackQueryHandler(self.button))
        dispatcher.add_handler(CommandHandler("help", self.help))
        dispatcher.add_handler(MessageHandler(Filters.text, self.fio))
        dispatcher.add_error_handler(self.error)

    def start(self, update, context):
        keyboard = [
            [InlineKeyboardButton("Получить новое задание", callback_data="task")],
            [
                InlineKeyboardButton(
                    "Добавить похищенного силовиками", callback_data="add_prisoner"
                )
            ],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Выберите опцию:", reply_markup=reply_markup)

    def add_prisoner(self, update, context):
        update.message.reply_text(text="Введите информацию о похищенном силовиками.")
        update.message.reply_text("Введите ФИО похищенного:")

    def search(self, update, context, prisoner_id, ovd_id):
        keyboard = [
            [
                InlineKeyboardButton(
                    "Нашёлся!",
                    callback_data="found" + "_" + str(prisoner_id) + "_" + str(ovd_id),
                )
            ],
            [
                InlineKeyboardButton(
                    "Нет:(",
                    callback_data="not_found" + "_" + str(prisoner_id) + "_" + str(ovd_id),
                )
            ],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text(
            "Позвоните в дежурную часть ОВД по указанным выше телефонами, дождитесь ответа, "
            + "задайте вопрос о пребывании похищенного в ОВД и укажите ответ:",
            reply_markup=reply_markup,
        )

    def fio(self, update, context):
        current_action = self.current_actions.get(update.message.chat.id)
        if current_action == "add_prisoner":
            prisoner_name = update.message.text
            db_add_prisoner(prisoner_name)
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Похищенный добавлен в базу для поиска.",
            )
            flag = False
            current_action = "start"
            start(update, context)
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Вы не завершили предыдущее действие.",
            )


    def process_task(self, update, context):
        (
            isTask,
            prisoner_id,
            prisoner_name,
            ovd_id,
            ovd_name,
            ovd_address,
            ovd_phones,
        ) = db_get_task(update.message.chat.id)
        if not isTask:
            update.message.reply_text(text="Нет поисковых заданий.")
            return False, None

        update.message.reply_text(
            text="Вы ищете похищенного силовиками. "
            + "Позвоните по всем указанным ниже телефоном с вопросом 'Не в вашем ли ОВД находится похищенный?'. "
            + "Памятка по звонкам в ОВД есть тут: www.example.com.\n"
            + "Данные: \n ФИО: {0}. \n Название ОВД: {1}. \n Телефоны ОВД: {2}. \n Адрес ОВД: {3}.".format(
                prisoner_name, ovd_name, ovd_phones, ovd_address
            )
        )
        self.search(update, context, prisoner_id, ovd_id)
        return True


    def process_finding(self, update, context):
        update.message.reply_text(
            text="Ура! Оповестите других волонтёров, звоните в ОВД-Инфо, собирайте передачки - инструкции на www.example.com."
        )
        li = update.data.split("_")
        prisoner_id = li[1]
        ovd_id = li[2]
        db_process_finding(prisoner_id, ovd_id)
        ids = db_get_prisoner_searchers(prisoner_id)
        # for id in ids:
        #     context.bot.send_message(chat_id=id, text="found")


    def process_not_finding(self, update, context):
        update.message.reply_text(
            text="Увы, похищенный пока не найден. Продолжайте поиски!"
        )
        li = update.data.split("_")
        prisoner_id = li[1]
        ovd_id = li[2]
        db_process_not_finding(prisoner_id, ovd_id)




    def button(self, update, context):
        current_action = self.current_actions.get(update.message.chat.id)
        query = update.callback_query

        if query.data == "task":
            if current_action == "start":
                tasks = process_task(query, context)
                if not tasks:
                    start(query, context)
                else:
                    current_action = "process_task"
            else:
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Вы не завершили предыдущее действие.",
                )
        elif query.data == "add_prisoner":
            if current_action == "start":
                add_prisoner(query, context)
                current_action = "add_prisoner"
            else:
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Вы не завершили предыдущее действие.",
                )
        elif query.data.startswith("found"):
            if current_action == "process_task":
                process_finding(query, context)
                current_action = "start"
                start(query, context)
            else:
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Вы не завершили предыдущее действие.",
                )
        else:
            if current_action == "process_task":
                process_not_finding(query, context)
                current_action = "start"
                start(query, context)
            else:
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Вы не завершили предыдущее действие.",
                )


    def help(self, update, context):
        update.message.reply_text("Введите /start.")


    def error(self, update, context):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, context.error)



def main(db, token=keys["TOKEN"], request_kwargs=REQUEST_KWARGS):
    bot = Bot(token, db, request_kwargs=request_kwargs)
    bot.updater.start_polling()
    bot.updater.idle()


# for testing purposes
if __name__ == "__main__":
    db = Database("sqlite:///:memory:")
    main(db)
