
from config import ADV_MESSAGE, EXP_TYPES_NAME

def text_add_foto(obj) -> str:
    text = ADV_MESSAGE['mess_ask_photo']
    if not hasattr(obj, 'butt_table'):
        text += ' ' + ADV_MESSAGE['mess_farther']
    else:
        text += ' ' + ADV_MESSAGE['mess_change']
    return text


def text_uno_elem(obj) -> str:
    text_by_type: dict = EXP_TYPES_NAME
    row = obj.butt_table.get(obj.step)
    el_type = row.vtype
    el_type_text = text_by_type.get(el_type)
    if not el_type_text:
        el_type_text = ''
    return f'Отправьте {el_type_text} для замены.'


def text_required_mess_type(types: str):
    base = 'На данном шаге можно отправить только '
    content = ''
    for key in types:
        content += EXP_TYPES_NAME.get(key, '') + ', '
    content = content[:-2]
    return base + content + '.'

def text_welcome_upd_mess(proces_obj) -> str:
    serial_num = proces_obj.adv_serial_num
    if not serial_num:
        return ADV_MESSAGE['mess_welcome_upd']
    return f"{ADV_MESSAGE['mess_welcome_upd']} №{serial_num}"
