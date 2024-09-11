from config import  (ADV_BLANK_WORDS as ABW, ADV_MESSAGE,
                     MESS_TEMPLATES, MAX_IN_MEDIA)

from typing import List

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
        
    return obj.adv_f_send


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

def get_message_type(message_obj) -> str:
    pass