import db_models as dbm

from copy import deepcopy
from datetime import datetime as dt

from config import  (ADV_BLANK_WORDS as ABW, ADV_MESSAGE,
                     MESS_TEMPLATES, MAX_IN_MEDIA)

from typing import List, Union
from sqlalchemy.orm import Session
from telebot.types import (InputMediaAudio, InputMediaDocument, 
                            InputMediaPhoto, InputMediaVideo)


def media_sorter(items: List[dict]) -> List[dict]:
    media_items = {
        'audio': [],
        'video': [],
        'document': [],
        'photo': []
    }
    input_media_class = {
        'audio': InputMediaAudio,
        'document': InputMediaDocument,
        'photo':  InputMediaPhoto,
        'video': InputMediaVideo
    }

    another_items = []
    result = []
    for item in items:
        content_type = item['content_type']
        if content_type in media_items.keys():
            class_type = input_media_class[content_type]
            media_items[content_type].append(
                class_type(
                    media=item[content_type],
                    caption=item['caption']
                )
            )
        else:
            another_items.append(item)
    
    for value in media_items.values():
        if not value:
            continue
        amount = len(value)
        if amount <= MAX_IN_MEDIA:
            result.append({'content_type': 'media', 'media': value})
        else:
            for i in range(MAX_IN_MEDIA, amount, MAX_IN_MEDIA):
                elements = value[i - MAX_IN_MEDIA : i]
                result.append({'content_type': 'media', 'media': elements})
            rest = value[i : amount]
            if rest:
                result.append({'content_type': 'media', 'media': rest})

    result.extend(another_items)
    return result


def adv_former(obj, template: str = MESS_TEMPLATES['adv_line']):
    adv_blank: dict = obj.adv_blank
    media_content = []
    single_texts = []
    obj.adv_f_send = []
    text = ''
    for key, value in adv_blank.items():
        if isinstance(value, (list, tuple)):
            media_content.append({key:value})
            continue
        elif isinstance(value, dict):
            if value['content_type'] == 'text':
                if key in obj.title_mess_content:
                    value = value['text']
                else:
                    value = '-' if not value else str(value)
                    single_texts.append({key:value})
            else:
                media_content.append({key:value})
                continue     
        value = '-' if not value else str(value)
        text += template.format(ABW[key], value)
    obj.adv_f_send.append({'text': text})
    obj.adv_f_send.extend(single_texts)
    
    for unit in media_content:
        key, value = list(unit.items())[0]
        if not value:
            continue
        if isinstance(value, dict):
            obj.adv_f_send.append({'text': template.format(ABW[key], ' ')})
            obj.adv_f_send.append(value)
        elif isinstance(value, (list, tuple)):
            obj.adv_f_send.append({'text': template.format(ABW[key], ' ')})
            out = media_sorter(value)
            if not out:
                obj.adv_f_send.append({'text': 'пусто'})
            else:
                obj.adv_f_send.extend(out)
        
    return deepcopy(obj.adv_f_send)


def review_elem(obj) -> dict:
    mess = {'text': '.'}
    row = obj.butt_table.get(obj.step)
    value = row.value.val
    if isinstance(value, (int, str)):
        mess = {'text': ADV_MESSAGE['before'] + str(value)}
    elif isinstance(value, dict):
        mess = value
    return mess


def get_or_create(session, model, create_params: dict,
                  filter_params: dict = {}):
    if not filter_params:
        filter_params = create_params
    instance = session.query(model).filter_by(**filter_params).first()
    if instance:
        return instance
    else:
        instance = model(**create_params)
        session.add(instance)
        session.commit()
        return instance


def reconst_blank(title_message, blank_template: dict) -> Union[dict, list]:
    composit_items = []
    for key, value in blank_template.items():
        if isinstance(value, (list, tuple)):
            composit_items.append(key)
            continue
        if hasattr(title_message, key):
            blank_template[key] = getattr(title_message, key)
    tg_mess_ids = [title_message.tg_mess_id]
    other = composit_items[0] if composit_items else None
    if other:
        container = blank_template[other]
        additional_messages = title_message.additional_messages

        #TODO выполнить сортировку внутри additional_messages по
        #sequence_num и enclousere num

        for mess in additional_messages:
            mess_value = mess.content_text
            reconst_mess = {
                'content_type': mess.mess_type,
                mess.mess_type: mess_value,
            }
            if mess.mess_type != 'text':
                reconst_mess.update({'caption': mess.caption})
            container.append(reconst_mess)
            tg_mess_ids.append(mess.tg_mess_id)
    return blank_template, tg_mess_ids



def adv_to_db(user, session: Session, sended_mess_objs: list):
    # user - это объект из модуля models.py
    db_user = get_or_create(
        session,
        dbm.User,
        create_params={'tg_id': user.id, 'name': user.name},
        filter_params={'tg_id': user.id})
    adv_blank = user.adv_proces.adv_blank
    title_mess_content = user.adv_proces.title_mess_content
    to_title_mess = {}
    objs_for_db = []
    for key in adv_blank.keys():
        if key in title_mess_content:
            data_key = adv_blank[key]['content_type']
            data = adv_blank[key][data_key]
            to_title_mess.update({key: data})
    
    current_datetime = dt.now()
    sended_title_mess = sended_mess_objs[0]
    title_message = dbm.TitleMessages(
        tg_mess_id = sended_title_mess.id,
        time=current_datetime,
        mess_type='text',
        user_id = db_user.id,
        **to_title_mess
    )
    session.add(title_message)
    session.commit()

    def _add_additional_message(mess_obj, conteiner:list,
                                sequence_num:int, enclosure_num:int):
        LINKED_TYPES = ('audio', 'voice', 'video', 'document', 'sticker')
        mess_type=mess_obj.content_type
        content_text = ''
        if mess_type == 'text':
            content_text = mess_obj.text
        elif mess_type == 'photo':
            content_text = mess_obj.photo[-1].file_id
        elif mess_type in LINKED_TYPES:
            content_text = getattr(mess_obj, mess_type).file_id

        additional_message = dbm.AdditionalMessages(
            tg_mess_id = mess_obj.id,
            time=current_datetime,
            mess_type=mess_type,
            caption=mess_obj.caption,
            content_text=content_text,
            title_message_id=title_message.id,
            sequence_num=sequence_num,
            enclosure_num=enclosure_num,
        )
        conteiner.append(additional_message)      
    sequence_num = 0    
    if len(sended_mess_objs) > 1:
        for mess_obj in sended_mess_objs[1: ]:
            enclosure_num = 0
            if not isinstance(mess_obj, list):
                _add_additional_message(mess_obj, objs_for_db,
                                        sequence_num, enclosure_num)
            else:
                for sub_mess in mess_obj:
                    _add_additional_message(sub_mess, objs_for_db,
                                            sequence_num, enclosure_num)
                    enclosure_num += 1
            sequence_num += 1
    advert = dbm.Adverts(
        external_id=user.adv_proces.adv_blank_id,
        title_message_id=title_message.id)
    objs_for_db.append(advert)
    session.add_all(objs_for_db)
    session.commit()


def make_title_mess(items: dict, template: str = MESS_TEMPLATES['adv_line']):
    title_mess = ''
    for key, value in items.items():
        text_elem = '-' if not value else str(value['text'])
        title_mess += template.format(ABW[key], text_elem)       
    return {'content_type': 'text', 'text': title_mess}


def prepare_changed(original_blank: dict, redacted_blank: dict,
                 title_mess_content: list, tg_mess_ids: list) -> dict:

    title_mess_items = {}
    deleted = []
    changed = []
    added_over = []
    is_title_changed = False
    additional_item_keys = []
    for key, value in original_blank.items():
        if key in title_mess_content:
            title_mess_items.update({key:value})
            if original_blank[key] != redacted_blank[key]:
                is_title_changed = True
        else:
            additional_item_keys.append(key)
    
    if is_title_changed:
        title_mess = make_title_mess(title_mess_items)
        changed.append(
            {'tg_id': tg_mess_ids[0], 'mess': title_mess}
        )
    
    num = 1
    for key in additional_item_keys:
        if isinstance(original_blank[key],(list, tuple)):
            am_original = len(original_blank[key])
            am_redacted = len(redacted_blank[key])
            if am_redacted > am_original:
                added_over.append(
                    {key: redacted_blank[key][am_original:am_redacted]}
                )
            elif am_redacted < am_original:
                for i in range(am_redacted):
                    if original_blank[key][i] != redacted_blank[key][i]:
                        changed.append(
                            {'tg_id': tg_mess_ids[num],
                             'mess': redacted_blank[key][i]}
                        )
                    num += 1
                for i in range(am_redacted, am_original):
                    deleted.append(
                        {'tg_id': tg_mess_ids[num],
                         'mess': original_blank[key][i]}
                        )
                    num += 1
        elif original_blank[key] != redacted_blank[key]:
            changed.append(
                {'tg_id': tg_mess_ids[num],
                 'mess': redacted_blank[key]}
            )
            num += 1

    return {'changed': changed, 'deleted': deleted, 'added_over': added_over}
