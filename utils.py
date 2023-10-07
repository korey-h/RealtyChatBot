from config import MESS_TEMPLATES, ADV_BLANK_WORDS as ABW
from models import RegistrProces

def adv_former(obj: RegistrProces, template: str = MESS_TEMPLATES['adv_line']):
    adv_blank: dict = obj.adv_blank
    text = ''
    for key, value in adv_blank.items():
        value = '-' if not value else str(value)
        text += template.format(ABW[key], value)
    obj.adv_f_send = text
    return text
