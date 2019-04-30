# -*- coding: utf-8 -*-
import telebot

import json
import urllib.request
from telebot import types
import flickr_api
from app import bot, AUTH_TOKEN, USER, BOT_TOKEN


@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Hi! I'm the FlickrBot and you can contact with Flickr through me."
                                      "To know more write /help or /info")


@bot.message_handler(commands=['help', 'info'])
def handle_help(message):
    bot.send_message(message.chat.id, "If you want to log in your account through me (for example to upload photos), "
                                      "write /auth.\n"
                                      "If you want to find smth, write /search.\n"
                                      "If you want to upload a photo to your account, write /upload.\n")


@bot.message_handler(commands=['auth', 'authorization'])
def handle_authorization(message):
    global AUTH_TOKEN, USER

    AUTH_TOKEN = flickr_api.auth.AuthHandler()
    url = AUTH_TOKEN.get_authorization_url("write")
    bot.send_message(message.chat.id, "Follow this link, log in and accept the query:" + url +
                                      "\nThen copy everything from the next web-page and send me.")

    @bot.message_handler(content_types=['text'])
    def handle_verifier(message2):
        global USER
        m = message2.text
        begin, end = m.find("<oauth_verifier>"), m.find("</oauth_verifier>")
        if begin != -1 and end != -1:
            AUTH_TOKEN.set_verifier(m[begin + 16:end])
            flickr_api.set_auth_handler(AUTH_TOKEN)
            USER = flickr_api.test.login()
            bot.send_message(message.chat.id, "You're authorised, let's start using me!"
                                              "\n(/help and /info are still available.)")
        else:
            bot.send_message(message.chat.id, "Wrong input, are you sure you're following my instructions?")


@bot.message_handler(commands=['search', 'find'])
def handle_search(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    itembtn1 = types.KeyboardButton('Person')
    itembtn2 = types.KeyboardButton('User')
    markup.add(itembtn1, itembtn2)
    bot.send_message(message.chat.id, "Choose one letter:", reply_markup=markup)

    @bot.message_handler(content_types=['text'])
    def handle_search_what(message2):
        pass


@bot.message_handler(commands=['upload'])
def handle_upload(message):
    global USER, AUTH_TOKEN
    if USER is None:
        bot.send_message(message.chat.id, "You're not authorized! Do it through /auth command")
        return
    bot.send_message(message.chat.id, "Send me your photo.")
    bot.register_next_step_handler(message, handle_upload_photo)


def handle_upload_photo(message):
    if len(message.photo) == 0:
        bot.send_message(message.chat.id, "There is no photo here! Send me a photo!")
        bot.register_next_step_handler(message, handle_upload_photo)
    photo = message.photo[-1]
    for x in message.photo:
        print(x.width, x.height)
    photo_id = photo.file_id
    url = "https://api.telegram.org/bot{}/getFile?file_id={}".format(BOT_TOKEN, photo_id)
    photo_path = json.loads(urllib.request.urlopen(url).read())['result']['file_path']
    url = "https://api.telegram.org/file/bot{}/{}".format(BOT_TOKEN, photo_path)
    with open("./tmp/pic.jpg".format(photo_path), 'wb') as pic:
        pic.write(urllib.request.urlopen(url).read())
    bot.send_message(message.chat.id, "Write a title.")
    bot.register_next_step_handler(message, handle_set_title)


def handle_set_title(message):
    flickr_api.upload(photo_file="./tmp/pic.jpg", title=message.text)
    bot.send_message(message.chat.id, "Photo is uploaded!")
