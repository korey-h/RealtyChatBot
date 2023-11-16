from config import MESS_TEMPLATES, ADV_BLANK_WORDS as ABW

def adv_former(obj, template: str = MESS_TEMPLATES['adv_line']):
    adv_blank: dict = obj.adv_blank
    separately = []
    obj.adv_f_send = []
    text = ''
    for key, value in adv_blank.items():
        if isinstance(value, (list, tuple)):
            separately.append({key:value})
            continue
        elif isinstance(value, dict):
            if value['content_type'] == 'text':
                value = value['text']
            else:
                separately.append({key:value})
                continue     
        value = '-' if not value else str(value)
        text += template.format(ABW[key], value)
    obj.adv_f_send.append({'text': text})

    for unit in separately:
        key, value = list(unit.items())[0]
        if not value:
            continue
        if isinstance(value, dict):
            obj.adv_f_send.append({'text': template.format(ABW[key], ':')})
            obj.adv_f_send.append(value)
        elif isinstance(value, (list, tuple)):
            obj.adv_f_send.append({'text': template.format(ABW[key], ':')})
            for item in value:
                obj.adv_f_send.append(item)
        
    return obj.adv_f_send
