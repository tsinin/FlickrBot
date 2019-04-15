# -*- coding: utf-8 -*-
import telebot
from app import bot, NAME, SURNAME, AGE


@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.from_user.id, 'Привет! Я - тестовый бот. Поговори со мной.')


@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.from_user.id, 'Напиши /reg')


@bot.message_handler(commands=['reg'])
def handle_reg(message):
    bot.send_message(message.from_user.id, "Как тебя зовут?")
    bot.register_next_step_handler(message, get_name)  # следующий шаг – функция get_name


# Handles all text messages that match the regular expression
@bot.message_handler(content_types=['text'], regexp="python")
def handle_python_message(message):
    bot.send_message(message.from_user.id, "Я обожаю python!")


@bot.message_handler(content_types=['text'])
def handle_text_message(message):
    bot.send_message(message.from_user.id, message.text)


def get_name(message):
    global NAME
    NAME = message.text
    bot.send_message(message.from_user.id, 'Какая у тебя фамилия?')
    bot.register_next_step_handler(message, get_surname)


def get_surname(message):
    global SURNAME
    SURNAME = message.text
    bot.send_message(message.from_user.id, 'Сколько тебе лет?')
    bot.register_next_step_handler(message, get_age)


def get_age(message):
    global AGE
    try:
        AGE = int(message.text)  # проверяем, что возраст введен корректно
    except (TypeError, ValueError):
        bot.send_message(message.from_user.id, 'Цифрами, пожалуйста')
    keyboard = telebot.types.InlineKeyboardMarkup()  # наша клавиатура
    key_yes = telebot.types.InlineKeyboardButton(text='Да', callback_data='yes')  # кнопка «Да»
    keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
    key_no = telebot.types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_no)
    question = 'Тебе {age} лет, тебя зовут {name} {surname}?'.format(age=AGE, name=NAME, surname=SURNAME)
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "yes":  # call.data это callback_data, которую мы указали при объявлении кнопки
        bot.send_message(call.message.chat.id, 'Запомню : )')
    elif call.data == "no":
        bot.send_message(call.message.chat.id, "Попробуем начать сначала. Как тебя зовут?")
        bot.register_next_step_handler(call.message, get_name)
