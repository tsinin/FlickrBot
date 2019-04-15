import telebot

bot = None

NAME = ''
SURNAME = ''
AGE = 0


def init_bot(token):
    global bot
    bot = telebot.TeleBot(token)

    from app import handlers
