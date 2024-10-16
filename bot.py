import json
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
from telebot.types import (InputMediaAudio, InputMediaDocument, 
                            InputMediaPhoto, InputMediaVideo)
from typing import List

import buttons as sb

from config import ALLOWED_BUTTONS, BUTTONS, EMOJI, MESSAGES
from models import User, RegistrProces
from utils import (adv_former, adv_to_db, is_sending_as_new, make_media,
                   prepare_changed, reconst_blank)

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


def send_multymessage(user_id, pre_mess: List[dict]):
    sent_messages = []
    for mess_data in pre_mess:
        content_type = mess_data.pop('content_type', None) or 'text'
        tg_mess_id = mess_data.pop('tg_mess_id', None)
        if content_type not in SEND_METHODS.keys():
            content_type = 'text'
        sender = SEND_METHODS[content_type]
        sent_mess = sender(user_id, **mess_data)
        sent_messages.append(sent_mess)
        mess_data.update({'content_type': content_type, 'tg_mess_id': tg_mess_id})

    return sent_messages


def adv_sender(mess, chat_id = my_chat_id, message_thread_id = my_thread_id):
    for item in mess:
        item.update({'message_thread_id': message_thread_id})
    return send_multymessage(chat_id, mess)




def is_buttons_alowwed(func_name: str, button_data: dict, user: User):
    btn_name = button_data.get('name')
    allowed = ALLOWED_BUTTONS.get(func_name)
    if not btn_name or allowed is None or btn_name not in allowed:
        text = MESSAGES['not_allowed_btn']
        bot.send_message(user.id, text=text)
        return False
    return True


@bot.message_handler(commands=['try_edit'])
#тестовая функция для проверки возможностей по редактированию сообщений
def try_edit(message, **kwargs):
    media_class = {
        'audio': InputMediaAudio,
        'document': InputMediaDocument,
        'photo':  InputMediaPhoto,
        'video': InputMediaVideo
    }
    self_name = 'try_edit'
    user = get_user(message)
    if user.is_stack_empty() or user.cmd_stack['cmd_name'] != self_name:
        user.cmd_stack = (self_name, try_edit)
        bot.send_message(user.id, text='высылай медиа!')
        return
    if len(user.storage) < 4:
        data = RegistrProces()._pars_mess_obj(message)
        user.storage.append(data)
    else:
        sent_messages = send_multymessage(user.id, user.storage)
        time.sleep(2)

        for i in range(len(user.storage)):
            mess_sent = sent_messages[len(user.storage) - i - 1]
            con_type = user.storage[i]['content_type']
            media_id = user.storage[i][con_type]
            media = media_class[con_type](media=media_id)
            if mess_sent.message_id != sent_messages[i].message_id:
                bot.edit_message_media(media, user.id, mess_sent.message_id)
            time.sleep(1)
        time.sleep(3)
        mess_for_del = sent_messages[0]
        bot.delete_message(user.id, mess_for_del.message_id)
        time.sleep(3)
        # mess_for_cor = sent_messages[1]
        # text_correct = 'новый текст'
        # bot.edit_message_text(text_correct, user.id, mess_for_cor.message_id)
    # text_orig = 'исходное сообщение'
    # text_correct = 'новый текст'

    # mess_sended = bot.send_message(user.id, text_orig)
    # bot.send_message(user.id, text_orig)
    # time.sleep(60)
    # bot.edit_message_text(text_correct, user.id, mess_sended.message_id)

@bot.message_handler(commands=['try_fake'])
#тестовая функция для проверки возможностей по редактированию сообщений
def try_fake(message, **kwargs):
    media_class = {
        'audio': InputMediaAudio,
        'document': InputMediaDocument,
        'photo':  InputMediaPhoto,
        'video': InputMediaVideo
    }
    self_name = 'try_fake'
    user = get_user(message)
    if user.is_stack_empty() or user.cmd_stack['cmd_name'] != self_name:
        user.cmd_stack = (self_name, try_fake)
        bot.send_message(user.id, text='высылай фото!')
        return
    if len(user.storage) < 1:
        data = RegistrProces()._pars_mess_obj(message)
        user.storage.append(data)
        bot.send_message(user.id, text='высылай документ!')
    elif len(user.storage) < 2:
        data = RegistrProces()._pars_mess_obj(message)
        user.storage.append(data)
    else:
        sent_messages = send_multymessage(user.id, user.storage)
        time.sleep(2)
        # text = 'Фотка тю-тю!'
        
        photo_id = sent_messages[0].message_id
        doc_id = sent_messages[1].message_id

        media_photo = media_class['photo'](media=photo_id)
        media_doc = media_class['document'](media=doc_id)
        bot.edit_message_media(media_photo, user.id, doc_id )
        time.sleep(2)
        bot.edit_message_media(media_doc, user.id, photo_id )





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
            bot.send_message(
                user.id,
                MESSAGES['mess_cancel_this'].format(up_stack['cmd_name']),
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
    cmd = user.get_cmd_stack()['cmd']
    context = [{'text': MESSAGES['renew_finished']}]
    del_error = False
    edit_error = False
    if cmd == redaction:
        if user.adv_proces:
            user.stop_upd()
            context = user.adv_proces.repeat_last_step()
        else:
            redacted_blank = user.upd_proces.clear_deleted()
            original_blank = user.upd_proces.original_blank
            title_mess_content = user.upd_proces.title_mess_content
            if is_sending_as_new(original_blank, redacted_blank,
                        title_mess_content):
                mess = adv_former(user.upd_proces)
                sended_mess_objs = adv_sender(mess)
                context = user.upd_proces.make_registration()
                user.upd_proces.adv_blank = user.upd_proces.wrapp_blank()
                adv_to_db(user, SESSION, sended_mess_objs)
                #TODO создать таблицу для связей нового и старого adv_blank_id
            else:
                res = prepare_changed(original_blank, redacted_blank,
                        title_mess_content,
                        user.upd_proces.tg_mess_ids)
                for tg_id in res['deleted'].keys():
                    try:
                        bot.delete_message(my_chat_id, tg_id)
                    except Exception:
                        del_error = True
                
                for tg_id, mess in res['changed'].items():
                    try:
                        if mess['content_type'] == 'text':
                            bot.edit_message_text(mess['text'], my_chat_id,
                                                  mess['tg_mess_id'])
                            continue
                        media = make_media(mess)
                        if not media:
                            edit_error = True
                            continue
                        bot.edit_message_media(media, my_chat_id,
                                                  mess['tg_mess_id'])
                    except Exception:
                        edit_error = True
                #TODO сохранение, удаление в базу данных
                if del_error or edit_error:
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
        sended_mess_objs = adv_sender(mess)
        adv_to_db(user, SESSION, sended_mess_objs)
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
    adv_blank, tg_mess_ids = reconst_blank(title_message, blank_template)
    user.start_update(adv_blank, tg_mess_ids, data)
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


@bot.message_handler(content_types=['photo', 'audio', 'document'])
def media_router(message):
    user = get_user(message)
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

    # db_user = get_or_create(SESSION, dbm.User, {'tg_id': 13333, 'name': "mey"})

    while True:
        try:
            bot.polling(non_stop=True)
        except Exception as error:
            if LET_VIEW_EXS:
                break
            err_info = error.__repr__()
            logger.exception(error)
            time.sleep(3)