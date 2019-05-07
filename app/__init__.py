import telebot
import flickr_api

BOT = None

BOT_TOKEN = None
AUTH_TOKENS = {}
USERS = {}
WALKERS = {}
FIRST_NUMS = {}
URLS = {}


def init_bot(token, flickr_keys):
    global BOT, BOT_TOKEN
    BOT_TOKEN = token
    BOT = telebot.TeleBot(token)
    flickr_api.set_keys(api_key=flickr_keys[0], api_secret=flickr_keys[1])

    from app import handlers
