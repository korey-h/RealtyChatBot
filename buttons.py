import json

from telebot.types import (InlineKeyboardButton, InlineKeyboardMarkup,
    KeyboardButton, ReplyKeyboardMarkup)

from config import BUTTONS, KEYWORDS


def name_to_cmd(names):
    return ['/' + name for name in names]


def make_base_kbd(buttons_name, row_width=3):
    keyboard = ReplyKeyboardMarkup(row_width=row_width, resize_keyboard=True)
    buttons = [KeyboardButton(name) for name in buttons_name]
    return keyboard.add(*buttons)


def make_welcome_kbd(*args, **kwargs):
    row_width = 2
    buttons_name = name_to_cmd(
        [BUTTONS['make_advert'],
         BUTTONS['help'], ]
        )
    return make_base_kbd(buttons_name, row_width)


def cancel_this_kbd(*args, **kwargs):
    buttons_name = name_to_cmd([
         BUTTONS['cancel_this']
        ])
    return make_base_kbd(buttons_name)


def pass_keyboard(*args, **kwargs):
    pass_button = InlineKeyboardButton(
        text=BUTTONS['pass'],
        callback_data=json.dumps(
            {'name': 'pass', 'payload': None}))
    return InlineKeyboardMarkup().add(pass_button)


def farther_keyboard(*args, **kwargs):
    pass_button = InlineKeyboardButton(
        text=BUTTONS['farther'],
        callback_data=json.dumps(
            {'name': 'farther', 'payload': None}))
    return InlineKeyboardMarkup().add(pass_button)

def send_btn(*args, **kwargs):
    pass_button = InlineKeyboardButton(
        text=BUTTONS['send_adv'],
        callback_data=json.dumps(
            {'name': 'send', 'payload': KEYWORDS['send_btn']}))
    return InlineKeyboardMarkup().add(pass_button)