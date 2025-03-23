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


def make_upd_kbd(*args, **kwargs):
    row_width = 3
    buttons_name = name_to_cmd(
        [BUTTONS['cancel_this'],
         BUTTONS['delete'],
         BUTTONS['apply'], ]
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
            {'name': 'pass', 'pld': None}))
    return InlineKeyboardMarkup().add(pass_button)


def farther_keyboard(obj, *args, **kwargs):
    if hasattr(obj, 'butt_table'):
        return
    pass_button = InlineKeyboardButton(
        text=BUTTONS['farther'],
        callback_data=json.dumps(
            {'name': 'farther', 'pld': None}))
    return InlineKeyboardMarkup().add(pass_button)


def send_btn(*args, **kwargs):
    send_button = InlineKeyboardButton(
        text=BUTTONS['send_adv'],
        callback_data=json.dumps(
            {'name': 'send', 'pld': KEYWORDS['send_btn']}))

    upd_button = InlineKeyboardButton(
        text=BUTTONS['redact'],
        callback_data=json.dumps(
            {'name': 'redact', 'pld': KEYWORDS['redact_btn']}))
    return InlineKeyboardMarkup().add(send_button, upd_button)


def renew_btn(*args, **kwargs):
    adv_blank_id = args[0]
    renew_button = InlineKeyboardButton(
        text=BUTTONS['renew'],
        callback_data=json.dumps(
            {'name': 'renew', 'pld': adv_blank_id}
        ))
    return InlineKeyboardMarkup().add(renew_button)


def welcome_upd_butt(obj, *args, **kwargs):
    buttons = []

    am_chapter_butts = len(obj.adv_blank)
    chapter_butts = [
        obj.butt_table.get(i) for i in range(1, am_chapter_butts + 1)]
    for butt_data in chapter_butts:
        button = InlineKeyboardButton(
        text=butt_data.title,
        callback_data=json.dumps(
            {'name': 'update', 'pld': butt_data.id}))
        buttons.append(button)
    return InlineKeyboardMarkup().add(*buttons)


def elements_butt(obj, *args, **kwargs):
    row = obj.butt_table.get(obj.step)
    # if not isinstance(row.value, list):
    if (not isinstance(row.value, list) and
            not isinstance(row.value.val, list)):
        return
    ids_for_out = obj.butt_table.relations.get(row.id)
    if not ids_for_out:
        return
    elif len(ids_for_out) == 1:
        ids_in_group = obj.butt_table.relations.get(ids_for_out[0])        
        ids_for_out = ids_in_group if ids_in_group else ids_for_out
    
    buttons = []
    for el_id in ids_for_out:
        el = obj.butt_table.get(el_id)
        if el is None:
            continue
        if el.value is None:
            continue
        button = InlineKeyboardButton(
        text=el.title,
        callback_data=json.dumps(
            {'name': 'update', 'pld': el.id}))
        buttons.append(button)
    return InlineKeyboardMarkup().add(*buttons)


def glue_keyboards(*args):
    keys = []
    for kbd in args:
        if kbd is None:
            continue
        new = unpuck_kbd(kbd)
        keys.extend(new)
    if keys:
        return InlineKeyboardMarkup().add(*keys)


def unpuck_kbd(kbd):
    keys = []
    if isinstance(kbd, list):
        for key in kbd:
            new = unpuck_kbd(key)
            keys.extend(new)
    else:
        keys.append(kbd)
    return keys

def glue_pre_mess(mess_1:dict, mess_2:dict):
    text = mess_1['text'] + '\n' + mess_2['text']
    reply_markup_1 = mess_1.get('reply_markup')
    reply_markup_2 = mess_2.get('reply_markup')
    reply_markup = glue_keyboards(
        reply_markup_1.keyboard if reply_markup_1 else None,
        reply_markup_2.keyboard if reply_markup_2 else None,
        )

    return {'text': text, 'reply_markup': reply_markup}

