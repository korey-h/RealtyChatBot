from config import MESS_TEMPLATES, ADV_BLANK_WORDS as ABW

def adv_former(obj, template: str = MESS_TEMPLATES['adv_line']):
    adv_blank: dict = obj.adv_blank
    text = ''
    for key, value in adv_blank.items():
        value = '-' if not value else str(value)
        text += template.format(ABW[key], value)
    obj.adv_f_send = text
    return text
