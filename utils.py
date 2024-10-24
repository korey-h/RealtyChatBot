import db_models as dbm

from copy import deepcopy
from datetime import datetime as dt

from config import  (ADV_BLANK_WORDS as ABW, ADV_MESSAGE, GROUP_TYPES,
                     MESS_TEMPLATES, MAX_IN_MEDIA)

from typing import List, Union
from sqlalchemy.orm import Session
from telebot import TeleBot
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


def adv_former(obj, template: str = MESS_TEMPLATES['adv_line'],
               insert_group_name=True):
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
            if insert_group_name:
                obj.adv_f_send.append(
                    {'text': template.format(ABW[key], ' ')})
            obj.adv_f_send.append(value)
        elif isinstance(value, (list, tuple)):
            if insert_group_name:
                obj.adv_f_send.append(
                    {'text': template.format(ABW[key], ' ')})
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
    db_mess_objs = {}
    for key, value in blank_template.items():
        if isinstance(value, (list, tuple)):
            composit_items.append(key)
            continue
        if hasattr(title_message, key):
            blank_template[key] = getattr(title_message, key)
    title_mess_id = int(title_message.tg_mess_id)
    tg_mess_ids = [title_mess_id]
    db_mess_objs[title_mess_id] = title_message

    other = composit_items[0] if composit_items else None
    if other:
        container = blank_template[other]
        additional_messages = title_message.additional_messages

        #TODO выполнить сортировку внутри additional_messages по
        #sequence_num и enclousere num

        for mess in additional_messages:
            mess_value = mess.content_text
            tg_mess_id = int(mess.tg_mess_id)
            db_mess_objs[tg_mess_id] = mess
            reconst_mess = {
                'content_type': mess.mess_type,
                mess.mess_type: mess_value,
                'tg_mess_id': tg_mess_id,
            }
            if mess.mess_type != 'text':
                reconst_mess.update({'caption': mess.caption})
            container.append(reconst_mess)
            tg_mess_ids.append(mess.tg_mess_id)
    return blank_template, tg_mess_ids, db_mess_objs



def adv_to_db(user, session: Session, sended_mess_objs: list):
    # user - это объект из модуля models.py
    db_user = get_or_create(
        session,
        dbm.User,
        create_params={'tg_id': user.id, 'name': user.name},
        filter_params={'tg_id': user.id})
    
    proces = user.adv_proces if user.adv_proces else user.upd_proces
    adv_blank = proces.adv_blank
    title_mess_content = proces.title_mess_content
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
        external_id=proces.adv_blank_id,
        title_message_id=title_message.id)
    objs_for_db.append(advert)
    session.add_all(objs_for_db)
    session.commit()


def make_title_mess(items: dict, tg_id: int, template: str = MESS_TEMPLATES['adv_line']):
    title_mess = ''
    for key, value in items.items():
        text_elem = '-' if not value else str(value)
        title_mess += template.format(ABW[key], text_elem)       
    return {'content_type': 'text', 'text': title_mess, 'tg_mess_id': tg_id}



def prepare_changed(original_blank: dict, redacted_blank: dict,
                 title_mess_content: list, tg_mess_ids: list) -> dict:

    title_mess_items = {}
    deleted = {}
    changed = {}
    title_raw = {}

    is_title_changed = False
    additional_item_keys = []

    def _glue_tg_ids(additional_item_keys: list, blank: dict) -> dict:
        ids_messages = {}
        def _catch_message(item:dict):
            tg_id = item.get('tg_mess_id')
            if tg_id:
                ids_messages.update({tg_id: item})
        
        for key in additional_item_keys:
            item = blank.get(key)
            if not item:
                continue
            if isinstance(item, dict):
                _catch_message(item)
            elif isinstance(item, list):
                for subitem in item:
                    _catch_message(subitem)
        return ids_messages                   

    for key, value in original_blank.items():
        if key in title_mess_content:
            title_mess_items.update({key:value})
            if original_blank[key] != redacted_blank[key]:
                title_mess_items[key] = redacted_blank[key]
                is_title_changed = True
        else:
            additional_item_keys.append(key)
    
    if is_title_changed:
        title_mess = make_title_mess(title_mess_items, tg_mess_ids[0])
        changed.update({tg_mess_ids[0]: title_mess})
        title_raw.update({tg_mess_ids[0]: title_mess_items})

    
    original_w_ids = _glue_tg_ids(additional_item_keys, original_blank)
    redacted_w_ids = _glue_tg_ids(additional_item_keys, redacted_blank)
   
    for id in original_w_ids.keys():
        red_mess = redacted_w_ids.get(id)
        orig_mess = original_w_ids.get(id)
        if not red_mess:
            deleted.update({id: orig_mess})
            continue
        if red_mess != orig_mess:
            changed.update({id: red_mess})
    
    return {'changed': changed, 'deleted': deleted, 'title_raw': title_raw}


def is_sending_as_new(original_blank: dict, redacted_blank: dict,
                 title_mess_content: list) -> bool:
 
    def _get_additional_item_keys(blank: dict,
                                  title_mess_content: list)-> list:
        additional_item_keys = []
        for key in blank.keys():
            if key in title_mess_content:
                continue
            additional_item_keys.append(key)
        return additional_item_keys
    
    def _group_by_type(items: list) -> dict:
        by_type_counter = {}
        for item in items:
            if not item:
                continue
            item_type = item['content_type']
            amount = by_type_counter.get(item_type)
            if amount:
                by_type_counter[item_type] += 1
            else:
                by_type_counter[item_type] = 1
        return by_type_counter
    
    def _is_excess(original: dict, redacted: dict) -> bool:
        for key, orig_value in original.items():
            red_value = redacted.get(key)
            if red_value and red_value > orig_value:
                return True

    orig_item_keys = _get_additional_item_keys(original_blank,
                                               title_mess_content)
    red_item_keys = _get_additional_item_keys(redacted_blank,
                                               title_mess_content)
    if len(red_item_keys) > len(orig_item_keys):
        return True
    
    for key, value in original_blank.items():
        if isinstance(value,(list, tuple)):
            orig_types = _group_by_type(value)
            red_types = _group_by_type(redacted_blank[key])
            orig_keys =  set(orig_types.keys())
            red_keys = set(red_types.keys())
            if red_keys.difference(orig_keys):
                return True
            if _is_excess(orig_types, red_types):
                return True
    return False


def make_media(mess: dict):
    media_classes = {
        'audio': InputMediaAudio,
        'document': InputMediaDocument,
        'photo':  InputMediaPhoto,
        'video': InputMediaVideo
    }
    content_type = mess['content_type']
    media_class = media_classes.get(content_type)
    if not media_class:
        return
    return media_class(media=mess[content_type])


def update_db_obj(db_mess_objs, tg_id: int, mess: dict):
    obj = db_mess_objs.get(tg_id)
    if not obj:
        return
    obj.update_from_tg_format(mess)


def update_messages(bot: TeleBot, chat_id: int, session: Session,
                    changed: dict, title_raw: dict, db_mess_objs):
    successful = True
    for tg_id, mess in changed.items():
        try:
            if mess['content_type'] == 'text':
                bot.edit_message_text(mess['text'], chat_id,
                                      mess['tg_mess_id'])         
            else:
                media = make_media(mess)
                if not media:
                    successful = False
                else:
                    bot.edit_message_media(media, chat_id,
                                           mess['tg_mess_id'])
        except Exception:
            successful = False

        if title_raw and title_raw.get(tg_id):
            mess = title_raw[tg_id]

        update_db_obj(db_mess_objs, tg_id, mess)
    session.commit()
    return successful


def delete_messages(bot: TeleBot, chat_id: int, session: Session,
                    deleted_ids: list):
    successful = True
    for tg_id in deleted_ids:
        try:
            bot.delete_message(chat_id, tg_id)
        except Exception:
            successful = False

    session.query(dbm.AdditionalMessages).filter(
        dbm.AdditionalMessages.tg_mess_id.in_(deleted_ids)
        ).delete(synchronize_session='evaluate')
    return successful


class SendingBlock():
    title_variants: dict = GROUP_TYPES

    def __init__(self, items: list, group_num:int, group_type: str):
        
        self.group_num = group_num
        self.group_type = group_type
        self.title = {}
        self.items = self._sort_enumerate_items(items)
    
    def find_set_title(self, titles: dict=None) -> dict:

        def _make_title(text: str) -> dict:
            return {
                'text': text,
                'content_type': 'text',
                'sequence_num': self.group_num,
                'enclosure_num': 0,
                }

        if not titles:
            text = self.title_variants.get(self.group_type)
            title = _make_title(text)
        else:        
            title = titles.get(self.group_num)
        self.title = title if title else _make_title(self.title_variants['universal'])
    
    def _sort_enumerate_items(self, items) -> list:
        max_num = 0
        no_number = []
        numerated = []
        for item in items:
            enclosure_num = item.get('enclosure_num')
            sequence_num = item.get('sequence_num')
            if not sequence_num:
                item['sequence_num'] = self.group_num
            if not enclosure_num:
                no_number.append(item)
                continue
            numerated.append(item)
            if enclosure_num > max_num:
                max_num = enclosure_num
        numerated.sort(key=lambda n: n['enclosure_num'] )

        for i, item in enumerate(no_number):
            item['enclosure_num'] = max_num + i + 1
        numerated.extend(no_number)

        return numerated

    def get_formated(self) -> list:
        out = [self.title]
        return out.extend(self.items)

