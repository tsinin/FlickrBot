# -*- coding: utf-8 -*-
import telebot

import json
import urllib.request
from telebot import types
import flickr_api
import os
from app import bot, AUTH_TOKENS, USERS, BOT_TOKEN, WALKERS, FIRST_NUMS, URLS

SIZES = [
    'Original',
    'Large 2048',
    'Large 1600',
    'Large',
    'Medium 800',
    'Medium 640',
    'Medium',
    'Small 320',
    'Small',
    'Thumbnail',
    'Large Square',
    'Square']


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
    global AUTH_TOKENS

    AUTH_TOKENS[hash(message.chat.id)] = flickr_api.auth.AuthHandler()
    url = AUTH_TOKENS[hash(message.chat.id)].get_authorization_url("write")
    bot.send_message(message.chat.id, "Follow this link, log in and accept the query:" + url +
                                      "\nThen copy everything from the next web-page and send me.")
    bot.register_next_step_handler(message, handle_verifier)


def handle_verifier(message):
    global USERS, AUTH_TOKENS
    m = message.text
    begin, end = m.find("<oauth_verifier>"), m.find("</oauth_verifier>")
    if begin != -1 and end != -1:
        AUTH_TOKENS[hash(message.chat.id)].set_verifier(m[begin + 16:end])
        flickr_api.set_auth_handler(AUTH_TOKENS[hash(message.chat.id)])
        USERS[hash(message.chat.id)] = flickr_api.test.login()
        os.system("mkdir ./users_data/{}".format(hash(message.chat.id)))
        AUTH_TOKENS[hash(message.chat.id)].save("./users_data/{}/auth_token.dat".format(hash(message.chat.id)))

        bot.send_message(message.chat.id, "You're authorised, let's start using me!"
                                          "\n(/help and /info are still available.)")
    else:
        bot.send_message(message.chat.id, "Wrong input, are you sure you're following my instructions?"
                                          "Let's try from the beginning")


@bot.message_handler(commands=['search', 'find'])
def handle_search(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    itembtn1 = types.KeyboardButton('Photos in search')
    itembtn2 = types.KeyboardButton('User')
    markup.add(itembtn1, itembtn2)
    bot.send_message(message.chat.id, "Choose what you want to find.", reply_markup=markup)
    bot.register_next_step_handler(message, handle_search_what)


def handle_search_what(message):
    if message.text == "User":
        bot.send_message(message.chat.id, "Write a user name, email or URL of the person.")
        bot.register_next_step_handler(message, handle_find_person)
    elif message.text == "Photos in search":
        bot.send_message(message.chat.id, "Write a tag or text to search by.")
        bot.register_next_step_handler(message, handle_find_photo)
    else:
        bot.send_message(message.chat.id, "Wrong input, are you sure you're following my instructions?"
                                          "If you want to continue, do everything from the start.")


def handle_find_person(message):
    global USERS
    person = None
    try:
        person = flickr_api.Person.findByUserName(message.text)
    except:
        pass
    if person is None:
        try:
            person = flickr_api.Person.findByEmail(message.text)
        except:
            pass
    if person is None:
        try:
            person = flickr_api.Person.findByUrl(message.text)
        except:
            pass
    if person is None:
        bot.send_message(message.chat.id, "There is no users with this name/email/URL.")
        return
    photos = None
    if USERS.get(hash(message.chat.id)) is None:
        photos = person.getPublicPhotos()
    else:
        photos = person.getPhotos()
    WALKERS[hash(message.chat.id)] = photos
    FIRST_NUMS[hash(message.chat.id)] = 0
    handle_print_3_photos_from_walker(message)


def handle_find_photo(message):
    global WALKERS, FIRST_NUMS
    WALKERS[hash(message.chat.id)] = flickr_api.Walker(flickr_api.Photo.search, text=message.text, content_type='1',
                                                       sort='interestingness-desc')
    FIRST_NUMS[hash(message.chat.id)] = 0
    handle_print_3_photos_from_walker(message)


def handle_print_3_photos_from_walker(message):
    global WALKERS, FIRST_NUMS
    if message.text == 'Stop':
        WALKERS[hash(message.chat.id)] = None
        FIRST_NUMS[hash(message.chat.id)] = None
        return
    i, j = FIRST_NUMS[hash(message.chat.id)], 0
    for photo in WALKERS[hash(message.chat.id)]:
        if j < i:
            j += 1
            continue
        else:
            j += 3
        size = None
        for size_std in SIZES:
            tmp = photo.getSizes().get(size_std)
            if tmp is not None:
                if int(tmp["width"]) * int(tmp["height"]) < 10 ** 6:
                    size = size_std
                    break
        try:
            bot.send_photo(message.chat.id, photo["sizes"][size]["source"])
        except:
            continue
        i += 1
        if i == FIRST_NUMS[hash(message.chat.id)] + 3:
            break
    FIRST_NUMS[hash(message.chat.id)] += 3
    markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    itembtn1 = types.KeyboardButton('Stop')
    itembtn2 = types.KeyboardButton('3 more photos')
    markup.add(itembtn1, itembtn2)
    bot.send_message(message.chat.id, "More or stop??", reply_markup=markup)
    bot.register_next_step_handler(message, handle_print_3_photos_from_walker)


@bot.message_handler(commands=['upload'])
def handle_upload(message):
    global USERS
    if USERS.get(hash(message.chat.id)) is None:
        try:
            flickr_api.set_auth_handler("./users_data/{}/auth_token.dat".format(hash(message.chat.id)))
            USERS[hash(message.chat.id)] = flickr_api.test.login()
        except:
            bot.send_message(message.chat.id, "You're not authorized! Do it through /auth command")
            return
    bot.send_message(message.chat.id, "Send me your photo.")
    bot.register_next_step_handler(message, handle_upload_photo)


def handle_upload_photo(message):
    global URLS
    if len(message.photo) == 0:
        bot.send_message(message.chat.id, "There is no photo here! Send me a photo!")
        bot.register_next_step_handler(message, handle_upload_photo)
    photo = message.photo[-1]
    photo_id = photo.file_id
    url = "https://api.telegram.org/bot{}/getFile?file_id={}".format(BOT_TOKEN, photo_id)
    photo_path = json.loads(urllib.request.urlopen(url).read())['result']['file_path']
    url = "https://api.telegram.org/file/bot{}/{}".format(BOT_TOKEN, photo_path)
    URLS[hash(message.chat.id)] = url
    bot.send_message(message.chat.id, "Write a title.")
    bot.register_next_step_handler(message, handle_set_title)


def handle_set_title(message):
    try:
        flickr_api.set_auth_handler("./users_data/{}/auth_token.dat".format(hash(message.chat.id)))
        USERS[hash(message.chat.id)] = flickr_api.test.login()
        flickr_api.upload(photo_file="Photo", title=message.text, photo_file_data=urllib.request.urlopen(URLS[hash(message.chat.id)]))
    except:
        bot.send_message(message.chat.id, "Oops! Error! Try later or try another photo.")
        return

    bot.send_message(message.chat.id, "Photo is uploaded!")
