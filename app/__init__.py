import telebot
import flickr_api

bot = None

BOT_TOKEN = None
AUTH_TOKEN = None
USER = None


def init_bot(token, flickr_keys):
    global bot
    global BOT_TOKEN
    BOT_TOKEN = token
    bot = telebot.TeleBot(token)
    flickr_api.set_keys(api_key=flickr_keys[0], api_secret=flickr_keys[1])

    from app import handlers
