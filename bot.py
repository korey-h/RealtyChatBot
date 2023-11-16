import json
import logging
import os
import threading
import time
from typing import List
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv
from telebot import TeleBot

import buttons as sb

from config import ALLOWED_BUTTONS, BUTTONS, EMOJI, MESSAGES
from models import User

if os.path.exists('.env'):
    load_dotenv('.env')
with open('about.txt', encoding='utf-8') as f:
    ABOUT = f.read()

LET_VIEW_EXS = True

my_chat_id = os.getenv('CHAT_ID')
my_thread_id = os.getenv('MESSAGE_THREAD_ID')
bot = TeleBot(os.getenv('TOKEN'))
SEND_METHODS = {
        'audio': bot.send_audio,
        'photo': bot.send_photo,
        'voice': bot.send_voice,
        'video': bot.send_video,
        'document': bot.send_document,
        'text': bot.send_message,
        'location': bot.send_location,
        'contact': bot.send_contact,
        'sticker': bot.send_sticker,
        }
users = {}

logger = logging.getLogger(__name__)
handler = RotatingFileHandler(
    'exceptions.log', maxBytes=50000000, backupCount=3)
logger.addHandler(handler)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

err_info = ''

def get_user(message) -> User:
    user_id = message.chat.id
    return users.setdefault(user_id, User(id=user_id))


def try_exec_stack(message, user: User, data):
    command = user.get_cmd_stack()
    if command and callable(command['cmd']):
        context = {
            'message': message,
            'user': user,
            'data': data,
            'from': 'stack'}
        command['cmd'](**context)
    else:
        bot.send_message(
            user.id, EMOJI['bicyclist'],
            reply_markup=sb.make_welcome_kbd())


def send_multymessage(user_id, pre_mess: List[dict]):
    for mess_data in pre_mess:
        content_type = mess_data.pop('content_type', None) or 'text'
        if content_type not in SEND_METHODS.keys():
            content_type = 'text'
        sender = SEND_METHODS[content_type]
        sender(user_id, **mess_data)
        mess_data.update({'content_type': content_type})


def adv_sender(mess, chat_id = my_chat_id, message_thread_id = my_thread_id):
    for item in mess:
        item.update({'message_thread_id': message_thread_id})
    send_multymessage(chat_id, mess)


def is_buttons_alowwed(func_name: str, button_data: dict, user: User):
    btn_name = button_data.get('name')
    allowed = ALLOWED_BUTTONS.get(func_name)
    if not btn_name or allowed is None or btn_name not in allowed:
        text = MESSAGES['not_allowed_btn']
        bot.send_message(user.id, text=text)
        return False
    return True


@bot.message_handler(commands=['start'])
def welcome(message):
    user = get_user(message)
    if user.is_stack_empty():
        mess = MESSAGES['welcome']
        bot.send_message(user.id, mess, reply_markup=sb.make_welcome_kbd())


@bot.message_handler(commands=[BUTTONS['help'], 'help'])
def about(message):
    user = get_user(message)
    bot.send_message(user.id, ABOUT)


@bot.message_handler(commands=[BUTTONS['cancel_this']])
def cancel_this(message):
    user = get_user(message)
    up_stack = user.cmd_stack_pop()
    if not up_stack or not up_stack['cmd_name']:
        return
    cmd = up_stack['cmd']
    if cmd == registration:
        user.stop_advert()
    all_comm = [cmd.__doc__, ]
    while up_stack:
        cmd = up_stack['cmd']
        prev = user.get_cmd_stack()
        if not prev or cmd != prev['called_by']:
            break
        user.cmd_stack_pop()
        all_comm.append(prev['cmd'].__doc__)
    out = ', '.join(all_comm)
    bot.send_message(
        user.id,
        MESSAGES['mess_cancel_this'].format(out),
        reply_markup=sb.make_welcome_kbd())


@bot.message_handler(commands=[BUTTONS['make_advert'], 'create'], )
def registration(message, user: User = None, data=None, *args, **kwargs):
    '''Оформление объявления'''

    self_name = 'advert_forming'
    user = user if user else get_user(message)
    called_from = kwargs.get('from')

    if not user.adv_proces:
        user.start_advert()
        user.set_cmd_stack((self_name, registration))
        if called_from and called_from == 'force_start':
            user.adv_proces.step += 1
    elif not called_from:
        return bot.send_message(
            user.id,
            text=MESSAGES['adv_always_on']
            )

    if isinstance(data, dict):
        if not is_buttons_alowwed(self_name, data, user):
            return
        data = data['payload'] if 'payload' in data.keys() else data
    crnt_step = user.adv_proces.step
    if (data is None and crnt_step > 0 and
            crnt_step < user.adv_proces._finish_step):
        context = user.adv_proces.pass_step()
    else:
        context = user.adv_proces.exec(data, mess_obj=message)
    if not context:
        return
    if not user.adv_proces.is_active:
        mess = user.adv_proces.adv_f_send
        adv_sender(mess)
        user.stop_advert()
        user.cmd_stack_pop()
    send_multymessage(user.id, context)


@bot.message_handler(content_types=['text'])
def text_router(message):
    user = get_user(message)
    data = message.text
    try_exec_stack(message, user, data)


@bot.message_handler(content_types=['photo', ])
def media_router(message):
    user = get_user(message)
    # photo = message.photo[-1].file_id # выбрать самое большое
    # caption = message.caption
    # bot.send_photo(user.id, photo=photo, caption=caption) #пробная отправка
    try_exec_stack(message, user, 'photo')


@bot.callback_query_handler(func=lambda call: True)
def inline_keys_exec(call):
    message = call.message
    user = get_user(message)
    data = json.loads(call.data)
    try_exec_stack(message, user, data)


##################################################################
def err_informer(chat_id):
    global err_info
    prev_err = err_info
    while True:
        if err_info == '' or err_info == prev_err:
            time.sleep(60)
            print('!', end=' ')
            continue
        prev_err = err_info
        try:
            bot.send_message(
                chat_id,
                f'Было выброшено исключение: {err_info}')
        except Exception:
            pass


if __name__ == '__main__':
    develop_id = os.getenv('DEVELOP_ID')
    t1 = threading.Thread(target=err_informer, args=[develop_id])
    t1.start()

    while True:
        try:
            bot.polling(non_stop=True)
        except Exception as error:
            if LET_VIEW_EXS:
                break
            err_info = error.__repr__()
            logger.exception(error)
            time.sleep(3)