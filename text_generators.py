
from config import ADV_MESSAGE

def text_add_foto(obj) -> str:
    text = ADV_MESSAGE['mess_ask_photo']
    if not hasattr(obj, 'butt_table'):
        text += ' ' + ADV_MESSAGE['mess_farther']
    else:
        text += ' ' + ADV_MESSAGE['mess_change']
    return text


def text_uno_elem(obj) -> str:
    text_by_type = {
        'audio': 'аудиофайл',
        'photo': 'фотографию',
        'voice': 'голосовое сообщение',
        'video': 'видео',
        'document': 'документ',
        'text': 'текст',
        'location': 'геопозицию',
        'contact': 'контакт',
        'sticker': 'стикер',       
    }
    row = obj.butt_table.get(obj.step)
    el_type = row.vtype
    el_type_text = text_by_type.get(el_type)
    if not el_type_text:
        el_type_text = ''
    return f'Отправьте {el_type_text} для замены.'
