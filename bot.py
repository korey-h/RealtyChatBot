import json
import inspect
import logging
import os
import sqlite3
import threading
import time

import db_models as dbm
import permissions as perms

from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from telebot import TeleBot
from typing import List

import buttons as sb

from config import ALLOWED_BUTTONS, BUTTONS,COMMANDS_NAME_RU, EMOJI, MESSAGES
from models import User, RegistrProces
from text_generators import text_required_mess_type
from utils import (adv_former, adv_to_db, delete_messages, is_sending_as_new,
                   make_adv_title, prepare_changed, reconst_blank, update_messages,
                   SendingBlock)

if os.path.exists('.env'):
    load_dotenv('.env')
else:
    print('файл .env с ключами доступа к боту, базе данны и т.п. не найден.')

LET_VIEW_EXS = True

my_chat_id = os.getenv('CHAT_ID')
my_thread_id = os.getenv('MESSAGE_THREAD_ID')
token = os.getenv('TOKEN')
bot = TeleBot(token)
DB_NAME = os.getenv('DB_NAME')
DB_PATH = os.getenv('DB_PATH')

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
        'media': bot.send_media_group,
        }

logger = logging.getLogger(__name__)
handler = RotatingFileHandler(
    'exceptions.log', maxBytes=50000000, backupCount=3)
logger.addHandler(handler)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

err_info = ''

users = {}
with open('about.txt', encoding='utf-8') as f:
    ABOUT = f.read()

if not os.path.isfile(DB_NAME):
    connection = sqlite3.connect(DB_NAME)
    connection.close()

engine = create_engine('sqlite:///'+DB_PATH+DB_NAME, echo=True)
SESSION = Session(engine)

def get_user(message) -> User:
    user_id = message.chat.id
    name = message.chat.username
    return users.setdefault(user_id, User(user_id, name))


def try_exec_stack(message, user: User, data, **kwargs):
    command = user.get_cmd_stack()
    if command and callable(command['cmd']):
        call_from = 'stack'
        if kwargs and kwargs.get('from'):
            call_from = kwargs.get('from')
        context = {
            'message': message,
            'user': user,
            'data': data,
            'from': call_from}
        command['cmd'](**context)
    else:
        bot.send_message(
            user.id, EMOJI['bicyclist'],
            reply_markup=sb.make_welcome_kbd())


def send_multymessage(user_id, pre_mess: List[dict], message_thread_id=None):
    sent_messages = []
    for mess_data in pre_mess:
        if isinstance(mess_data, SendingBlock):
            enclusive_data = mess_data.get_for_sending()
            if not enclusive_data:
                continue
            sent_part = send_multymessage(user_id, enclusive_data)
            mess_data.set_ids(sent_part)
            sent_messages.extend(sent_part)
            continue

        content_type = mess_data.get('content_type') or 'text'
        if content_type not in SEND_METHODS.keys():
            content_type = 'text'
        sender = SEND_METHODS[content_type]
        args = inspect.getfullargspec(sender).args
        sender_data = {}
        for key, value in mess_data.items():
            if key in args:
                sender_data.update({key:value})
        sent_mess = sender(user_id, message_thread_id=message_thread_id, **sender_data)
        sent_messages.append(sent_mess)

    return sent_messages


def adv_sender(pre_mess: List[dict], proces_obj: RegistrProces,
               chat_id: int = my_chat_id, message_thread_id: int = my_thread_id):
    if not proces_obj.adv_serial_num:
        serial = dbm.AdvertSerialNums()
        SESSION.add(serial)
        SESSION.commit()
        proces_obj.adv_serial_num = serial.id
    else:
        serial = SESSION.query(dbm.AdvertSerialNums).filter(
                    dbm.AdvertSerialNums.id==proces_obj.adv_serial_num).first()
    title_title ={
            'text': make_adv_title(proces_obj.adv_serial_num),
            'content_type': 'text',
            'blank_line_name': 'title',
            'sequence_num': 0,
            'enclosure_num': 0,
            'serial_obj': serial,
            'parse_mode': 'html'
            }
    
    for mess in pre_mess:
        if isinstance(mess, SendingBlock): # TODO упростить; титульный блок должен быть всегда первым
            if mess.group_num == 0:
                mess.title = title_title
                break
    return send_multymessage(chat_id, pre_mess, message_thread_id)


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
    elif cmd == redaction:
        if user.adv_proces:
            context = user.adv_proces.repeat_last_step()
            send_multymessage(user.id, context)
        else:
            cmd_name = up_stack['cmd_name']
            translated = COMMANDS_NAME_RU.get(cmd_name)
            cmd_name = translated if translated else cmd_name
            bot.send_message(
                user.id,
                MESSAGES['mess_cancel_this'].format(cmd_name),
                reply_markup=sb.make_welcome_kbd())
        user.stop_upd()
        return

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


@bot.message_handler(commands=['break', 'Завершить_все'])
def cancel_all(message):
    user = get_user(message)
    user.cancel_all()
    bot.send_message(
        user.id, MESSAGES['cancel_all'],
        reply_markup=sb.make_welcome_kbd())


@bot.message_handler(commands=[BUTTONS['apply']])
def apply_update(message):
    user = get_user(message)
    up_stack = user.get_cmd_stack()
    if not up_stack:
        return
    cmd = up_stack['cmd']
    context = [{'text': MESSAGES['renew_finished']}]
    del_success = True
    upd_success = True

    if cmd == redaction:
        if user.adv_proces:
            context = user.adv_proces.repeat_last_step()
        else:
            redacted_blank = user.upd_proces.adv_blank
            original_blank = user.upd_proces.original_blank
            title_mess_content = user.upd_proces.title_mess_content
            if is_sending_as_new(original_blank, redacted_blank,
                        title_mess_content):
                mess = adv_former(user.upd_proces)
                sended_mess_objs = adv_sender(mess, user.upd_proces)
                user.upd_proces.make_registration()
                context = user.upd_proces.finish_message
                adv_to_db(user, SESSION, sended_mess_objs)
                #TODO создать таблицу для связей нового и старого adv_blank_id
            else:
                res = prepare_changed(original_blank, redacted_blank,
                        title_mess_content,)
                deleted_ids = list(res['deleted'].keys())
                if deleted_ids:
                    del_success = delete_messages(bot, my_chat_id, SESSION,
                                                deleted_ids)
                
                changed = res['changed']
                title_raw = res['title_raw']
                if changed:
                    db_mess_objs = user.upd_proces.db_mess_objs
                    upd_success = update_messages(bot, my_chat_id, SESSION,
                                                  changed, title_raw, db_mess_objs )

                if not del_success or not upd_success:
                    context.append({'text': MESSAGES['renew_tg_error']})
        user.stop_upd()
    user.cmd_stack_pop()
    send_multymessage(user.id, context)


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

    received_mess_type = message.content_type
    expected_mess_type = user.adv_proces.step_exp_types()
    if expected_mess_type and received_mess_type not in expected_mess_type:
        return bot.send_message(
            user.id,
            text=text_required_mess_type(expected_mess_type)
            )

    if isinstance(data, dict):
        if not is_buttons_alowwed(self_name, data, user):
            return
        data = data['pld'] if 'pld' in data.keys() else data
        if data == 'redact' and (
                user.adv_proces.step == user.adv_proces.send_step):
            redaction(message, user, **{'from':self_name})
            return
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
        try:
            sended_mess_objs = adv_sender(mess, user.adv_proces)
        except:
            user.adv_proces.is_active = True
            user.adv_proces.repeat_last_step()
            return bot.send_message(
                user.id,
                text=MESSAGES['fault_finish_sending']
                )
        adv_to_db(user, SESSION, sended_mess_objs)
        context = user.adv_proces.finish_message
        user.stop_advert()
        user.cmd_stack_pop()
    send_multymessage(user.id, context)


@bot.message_handler(commands=['correct'], )
def redaction(message, user: User = None, data=None, *args, **kwargs):
    '''Редактирование объявления'''

    self_name = 'advert_update'
    user = user if user else get_user(message)
    called_from = kwargs.get('from')

    if not user.upd_proces:
        user.update_advert()
        user.set_cmd_stack((self_name, redaction))

    elif not called_from:
        return bot.send_message(
            user.id,
            text=MESSAGES['adv_always_on']
            )
    elif called_from == 'delete':
        context = user.upd_proces.delete()
        send_multymessage(user.id, context)
        return
    
    elif called_from == 'find_mess_for_renew':
        user.set_cmd_stack((self_name, redaction))

    received_mess_type = message.content_type
    expected_mess_type = user.upd_proces.step_exp_types()
    if expected_mess_type and received_mess_type not in expected_mess_type:
        return bot.send_message(
            user.id,
            text=text_required_mess_type(expected_mess_type)
            )

    if isinstance(data, dict):
        if not is_buttons_alowwed(self_name, data, user):
            return
        context = user.upd_proces.exec(data)
    else:
        context = user.upd_proces.exec(data, mess_obj=message)
    if not context:
        return
    send_multymessage(user.id, context)


@bot.message_handler(commands=['renew', BUTTONS['renew']])
def find_mess_for_renew(message, user: User = None, data=None, *args, **kwargs):
    """Поиск объявления"""
    self_name = 'find_mess_for_renew'
    user = user if user else get_user(message)
    called_from = kwargs.get('from')

    if not called_from:
        if user.is_stack_empty():
            user.set_cmd_stack(
                {'cmd_name': self_name,
                'cmd':find_mess_for_renew,
                'data':{},
                'called_by': {}})
            return bot.send_message(
                        user.id,
                        text=MESSAGES['adv_search'])
        else:
            return bot.send_message(
                    user.id,
                    text=MESSAGES['cancel_other'])
    if data is None:
        return bot.send_message(
            user.id,
            text=MESSAGES['await_search_code'])
    advert = SESSION.query(dbm.Adverts).filter(
                        dbm.Adverts.external_id==data).first()
    if not advert:
        return bot.send_message(
            user.id,
            text=MESSAGES['no_adverts'])
    
    title_message = SESSION.query(dbm.TitleMessages).filter(
                        dbm.TitleMessages.id==advert.title_message_id).first()
    if not title_message:
        return bot.send_message(
            user.id,
            text=MESSAGES['advert_is_lost'])        
    
    if not perms.has_redaction_permission(title_message, user.id):
        return bot.send_message(
            user.id,
            text=MESSAGES['no_redact_permissions'])
    
    if not perms.is_resend_while_redaction_active(user):
        return bot.send_message(
            user.id,
            text=MESSAGES['redact_period_ended'])
    
    if not perms.is_redac_available_again(user):
         return bot.send_message(
            user.id,
            text=MESSAGES['redact_too_often'])       

    blank_template = RegistrProces().adv_blank.copy()
    title_mess_content = RegistrProces().title_mess_content
    adv_blank, db_mess_objs = reconst_blank(title_message, blank_template,
                                            title_mess_content)
    user.start_update(adv_blank=adv_blank, adv_blank_id=data,
                      db_mess_objs=db_mess_objs)
    user.upd_proces.adv_serial_num = title_message.serial_info.id
    user.cmd_stack_pop()
    redaction(message, user, **{'from': 'find_mess_for_renew'})


@bot.message_handler(commands=['delete', BUTTONS['delete']], )
def delete(message, user: User = None, data=None):
    user = get_user(message)
    kwargs = {'from': 'delete'}
    try_exec_stack(message, user, data, **kwargs)


@bot.message_handler(content_types=['text'])
def text_router(message):
    user = get_user(message)
    data = message.text
    try_exec_stack(message, user, data)


@bot.message_handler(content_types=['photo', 'audio', 'document', 'location'])
def media_router(message):
    user = get_user(message)
    try_exec_stack(message, user, 'photo')


@bot.callback_query_handler(func=lambda call: True)
def inline_keys_exec(call):
    message = call.message
    user = get_user(message)
    data = json.loads(call.data)
    name = data.get('name')
    if name and name == 'renew':
        adv_ext_id = data.get('pld')
        return find_mess_for_renew(message, user, adv_ext_id, **{'from':inline_keys_exec})
    else:
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