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

from db_models import TitleMessages, AdditionalMessages


def review_elem(obj) -> dict:
    mess = {'text': '.'}
    row = obj.butt_table.get(obj.step)
    value = row.value.raw

    if value['content_type'] == 'text':
        text = str(value['text'])
        if not text:
            text = '---'
        mess = {
            'content_type': 'text',
            'text': ADV_MESSAGE['before'] + text,}
    else:
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
    adv_f_send = proces.adv_f_send

    for key, item in adv_blank.items():
        if key not in title_mess_content:
            continue
        to_title_mess.update({key: item['text']})
    
    current_datetime = dt.now()
    title_mess_tg_id = adv_f_send[0].items[0]['tg_mess_id']
    title_message = dbm.TitleMessages(
        tg_mess_id = title_mess_tg_id,
        time=current_datetime,
        mess_type='text',
        user_id = db_user.id,
        **to_title_mess
    )
    session.add(title_message)
    session.commit()
    objs_for_db = []

    for block in adv_f_send[1:]:
        for params in block.get_for_db():
            additional_message = dbm.AdditionalMessages(
                time=current_datetime,
                title_message_id=title_message.id,
                **params,
            )
            objs_for_db.append(additional_message)

    advert = dbm.Adverts(
        external_id=proces.adv_blank_id,
        title_message_id=title_message.id)
    objs_for_db.append(advert)
    session.add_all(objs_for_db)
    session.commit()


def make_title_mess(items: dict, tg_id: int, template: str = MESS_TEMPLATES['adv_line']):
    title_mess = ''
    for key, value in items.items():
        text_elem = '-' if not value else str(value['text'])
        title_mess += template.format(ABW[key], text_elem)       
    return {'content_type': 'text', 'text': title_mess, 'tg_mess_id': tg_id}


def make_title_f_blank(proces_obj, template: str = MESS_TEMPLATES['adv_line']):
    items = {key:proces_obj.adv_blank[key]['text'] for key in proces_obj.title_mess_content}
    title_mess = ''
    for key, value in items.items():
        text_elem = '-' if not value else str(value)
        title_mess += template.format(ABW[key], text_elem)
    title = {'content_type': 'text', 'text': title_mess, }
    return SendingBlock(
            [title],
            blank_line_name='title',
            group_num=0,
            group_type='text',
            ignore_title=True)


def prepare_changed(original_blank: dict, redacted_blank: dict,
                 title_mess_content: list, tg_mess_ids: list = []) -> dict:

    title_mess_items = {}
    deleted = {}
    changed = {}
    title_raw = {}
    donors = {}
    is_title_changed = False
    additional_item_keys = []

    def _glue_tg_ids(additional_item_keys: list, blank: dict) -> dict:
        ids_messages = {}
        new = {}
        def _catch_message(item:dict):
            tg_id = item.get('tg_mess_id')
            if tg_id:
                ids_messages[tg_id] = item
            else:
                item_type = item['content_type']
                new.setdefault(item_type,[])
                new[item_type].append(item)
        
        for key in additional_item_keys:
            item = blank.get(key)
            if not item:
                continue
            if isinstance(item, dict):
                _catch_message(item)
            elif isinstance(item, list):
                for subitem in item:
                    subitem_type = subitem['content_type']
                    if subitem is None or subitem[subitem_type] is None:
                        continue
                    _catch_message(subitem)
        return ids_messages, new                   

    for key, value in original_blank.items():
        if key in title_mess_content:
            title_mess_items[key] = value
            if original_blank[key] != redacted_blank[key]:
                title_mess_items[key] = redacted_blank[key]
                title_mess_tg_id = original_blank[key]['tg_mess_id']
                is_title_changed = True
        else:
            additional_item_keys.append(key)
    
    if is_title_changed:
        title_mess = make_title_mess(title_mess_items, title_mess_tg_id)
        changed[title_mess_tg_id] = title_mess
        title_raw[title_mess_tg_id] = title_mess_items

    
    original_w_ids, new = _glue_tg_ids(additional_item_keys, original_blank)
    redacted_w_ids, new = _glue_tg_ids(additional_item_keys, redacted_blank)
   
    for id in original_w_ids.keys():
        red_mess = redacted_w_ids.get(id)
        orig_mess = original_w_ids.get(id)
        mess_type = orig_mess['content_type']
        if not red_mess or not red_mess[mess_type]:
            deleted[id] = orig_mess
            donors.setdefault(mess_type,[])
            donors[mess_type].append(orig_mess)
        elif red_mess[mess_type] != orig_mess[mess_type]:
            changed[id] = red_mess
    
    for key, items in new.items():
        for item in items:
            donor = donors[key].pop()
            item.update({
                'tg_mess_id': donor['tg_mess_id'],
                'db_id': donor['db_id'],
            })
            changed[donor['tg_mess_id']] = item
            deleted.pop(donor['tg_mess_id'])
    
    return {'changed': changed, 'deleted': deleted, 'title_raw': title_raw}


def is_sending_as_new(original_blank: dict, redacted_blank: dict,
                 title_mess_content: list) -> bool:
    
    def _count_by_type(items: list) -> dict:
        by_type_counter = {}
        for item in items:
            if item is None:
                continue
            item_type = item['content_type']
            if item[item_type] is None:
                continue
            by_type_counter.setdefault(item_type,0)
            by_type_counter[item_type] += 1
        return by_type_counter
    
    def _is_excess(original: dict, redacted: dict) -> bool:
        for key, orig_value in original.items():
            red_value = redacted.get(key)
            if not red_value:
                return
            if red_value > orig_value:
                return True

    for key, value in original_blank.items():
        if isinstance(value,(list, tuple)):
            orig_types = _count_by_type(value)
            red_types = _count_by_type(redacted_blank[key])
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


def update_db_obj(db_mess_objs: Union[TitleMessages, AdditionalMessages], tg_id: int, mess: dict):
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

    deleted = session.query(dbm.AdditionalMessages).filter(
        dbm.AdditionalMessages.tg_mess_id.in_(deleted_ids)
        ).delete(synchronize_session='evaluate')
    session.commit()
    return successful


class SendingBlock():
    blank_titles: dict = ABW
    universal_title = 'В том числе'
    media_classes = {
        'audio': InputMediaAudio,
        'document': InputMediaDocument,
        'photo':  InputMediaPhoto,
        'video': InputMediaVideo
    }
    max_media = MAX_IN_MEDIA
    allowed_content = ('audio', 'voice', 'video', 'document', 'text')

    def __init__(self, items: List[dict],blank_line_name:str, group_num:int, 
                 group_type: str, title: dict={}, ignore_title: bool=False,
                 max_len_text = 250):
        self.blank_line_name = blank_line_name
        self.group_num = group_num
        self.group_type = group_type
        self.max_len_text = max_len_text
        self.title = title if title else self._make_title()
        self.items: list = self._sort_enumerate_items(items)
        self.ignore_title = ignore_title
        self.formated = []
        self.media_extra_args = {}
  

    def _make_title(self) -> dict:
        text = self.blank_titles.get(self.blank_line_name)
        if not text:
            text = str(self.blank_line_name) + '. ' + self.universal_title
        return {
            'text': text,
            'content_type': 'text',
            'blank_line_name': self.blank_line_name,
            'sequence_num': self.group_num,
            'enclosure_num': 0,
            }

    def _sort_enumerate_items(self, items: List[dict]) -> list:
        if self.group_type == 'text':
            cleaned = self._exclude_title(items)
            if not cleaned:
                return []
            items = self._combine_texts(cleaned)
        max_num = 0
        no_number = []
        numerated = []
        for item in items:
            if not item or item['content_type'] is None:
                continue
            sequence_num = item.get('sequence_num')
            enclosure_num = item.get('enclosure_num')
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

    def _devide_media(self, items):
        out = []
        amount = len(items)
        if amount <= self.max_media:
            out.append({'content_type': 'media', 'media': items})
        else:
            for i in range(self.max_media, amount, self.max_media):
                elements = items[i - self.max_media : i]
                out.append({'content_type': 'media', 'media': elements})
            rest = items[i : amount]
            if rest:
                out.append({'content_type': 'media', 'media': rest})
        return out

    def _exclude_title(self, items: List[dict]):
        cleaned = []
        for item in items:
            if item.get('enclosure_num') == 0:
                continue
            cleaned.append(item)
        return cleaned

    def _combine_texts(self, texts: List[dict]) -> List[dict]:
        texts = self._divide_single_text(texts)
        parts = []
        part_len = 0
        text_part = ''
        for item in texts:
            text = item['text']
            part_len += len(text)
            if part_len > self.max_len_text:
                parts.append({'content_type': 'text', 'text': text_part})
                text_part = text + '\n'
                part_len = len(text)
            else:
                text_part += text
        parts.append({'content_type': 'text', 'text': text_part[:-1]})
        return parts
    
    def _divide_single_text(self, texts: List[dict]) -> List[dict]:
        result = []
        for item in texts:
            text = item['text']
            if len(text) <= self.max_len_text:
                result.append(item)
            else:
                start = 0
                text_len = len(text)
                while start < text_len:
                    end = start + self.max_len_text
                    end = end if end < text_len else text_len
                    part = text[start: end]
                    start = end
                    result.append({'content_type': 'text', 'text': part})
        return result

    def to_media_class(self):
        converted = []
        class_type = self.media_classes[self.group_type]
        for item in self.items:
            caption = item.get('caption')
            body = item[self.group_type]
            instance = class_type(media=body, caption=caption)
            self.media_extra_args[instance] = item
            converted.append(instance)
        return converted

    def get_formated(self) -> list:
        out = []
        if not self.ignore_title:
            out = [self.title,]

        if self.group_type in self.media_classes.keys():
            conv_to_media = self.to_media_class()
            divided_into_parts = self._devide_media(conv_to_media)
            out.extend(divided_into_parts)
        else:
            out = self.items
        self.formated = out
        return out

    def get_for_sending(self):
        return self.get_formated()


    def get_for_db(self) -> List[dict]:
        out = []
        if not self.ignore_title:
            out = [{
                'mess_type': 'text',
                'caption': None,
                'content_text': self.title['text'],
                'sequence_num': self.title['sequence_num'],
                'enclosure_num': self.title['enclosure_num'],
                'tg_mess_id': self.title['tg_mess_id'],
                'blank_line_name': self.blank_line_name,
            },]
        for item in self.items:
            out.append({
                'mess_type': item['content_type'],
                'caption': item.get('caption'),
                'content_text': item[item['content_type']],
                'sequence_num': item['sequence_num'],
                'enclosure_num': item['enclosure_num'],
                'tg_mess_id': item['tg_mess_id'],
                'blank_line_name': self.blank_line_name,
            })
        return out
    
    def set_ids(self, sent_messages=list):
        offset = 0
        if not self.ignore_title:
            self.title['tg_mess_id'] = sent_messages[0].id
            offset = 1
        for i, message in enumerate(sent_messages):
            if i < offset:
                continue
            if self.formated[i]['content_type'] == 'media':
                conten_media = self.formated[i]['media']
                for num, instance in enumerate(conten_media):
                    self.media_extra_args[instance]['tg_mess_id'] = message[num].id
            else:
                self.formated[i]['tg_mess_id'] = message.id


def content_sorter(items: List[dict], blank_line_name:str) -> list:
    by_types = {
        'audio': [],
        'video': [],
        'document': [],
        'photo': [],
        'text': []
    }    
    result = []
    for item in items:
        content_type = item['content_type']
        if content_type in by_types.keys():
            by_types[content_type].append(item)
    group_num = 0
    ignore_title = False
    for key, items in by_types.items():
        if not items:
            continue
        block = SendingBlock(
            items=items,
            blank_line_name=blank_line_name,
            group_num=group_num,
            group_type=key,
            ignore_title=ignore_title
        )
        group_num =+ 1
        ignore_title = True
        result.append(block)
    return result


def adv_former(obj):
    adv_blank: dict = obj.adv_blank
    title_mess = make_title_f_blank(obj)
    obj.adv_f_send = [title_mess]
    for key, value in adv_blank.items():
        if key in obj.title_mess_content:
            continue
        if isinstance(value, dict):
            block = SendingBlock(
                items=[value],
                blank_line_name=key,
                group_num=0,
                group_type=value['content_type'],
                ignore_title=True
            )
            obj.adv_f_send.append(block)
        elif isinstance(value, list):
            blocks = content_sorter(value, key)
            obj.adv_f_send.extend(blocks)
    return obj.adv_f_send


def reconst_blank(title_message:TitleMessages, blank_template: dict,
                   title_mess_content: list) -> Union[dict, list]:
    
    title_mess_id = title_message.tg_mess_id
    db_mess_objs = {title_mess_id:title_message, }
    for key in title_mess_content:
        blank_template[key] = {
            'content_type': 'text',
            'text': getattr(title_message, key),
            'tg_mess_id': title_message.tg_mess_id,
            'db_id': title_message.id
        }

    additional_messages: List[AdditionalMessages] = title_message.additional_messages
    container = {}
    for mess in additional_messages:
        tg_mess_id = int(mess.tg_mess_id)
        db_mess_objs[tg_mess_id] = mess
        blank_line_name = mess.blank_line_name
        if not container.get(blank_line_name):
            container[blank_line_name] = []
        container[blank_line_name].append({
            'content_type': mess.mess_type,
            'caption': mess.caption,
            mess.mess_type: mess.content_text,
            'sequence_num': mess.sequence_num,
            'enclosure_num': mess.enclosure_num,
            'blank_line_name': blank_line_name, 
            'tg_mess_id': mess.tg_mess_id,
            'db_id': mess.id
        })
    for key, value in container.items():
        value.sort(
            key=lambda mess:
                str(mess['sequence_num']) + str(mess['enclosure_num'])
            )
        blank_template[key] = value
    
    return blank_template, db_mess_objs