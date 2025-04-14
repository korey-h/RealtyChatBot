import buttons as sb
import text_generators as ttg
import validators as vlds

from config import ADV_MESSAGE


adv_blank = {
    'space': None,
    'flour': None,
    'material': '',
    'address': '',
    'year': None,
    'district': '',
    'price': None,
    'photo': [],
}

title_mess_content = [
    'space', 'flour', 'material',
    'address','year', 'district','price',
]

step_actions = {
        1: {'name': 'space', 'required': True},
        2: {'name': 'flour', 'required': True},
        3: {'name': 'material', 'required': True},
        4: {'name': 'address', 'required': True},
        5: {'name': 'year', 'required': True},
        6: {'name': 'district', 'required': False},
        7: {'name': 'price', 'required': True},
        8: {'name': 'photo', 'required': False},
    }

step_messages = {
        1: [{'text': ADV_MESSAGE['mess_ask_space']}],
        2: [{'text': ADV_MESSAGE['mess_ask_flour']}],
        3: [{'text': ADV_MESSAGE['mess_ask_material']}],
        4: [{'text': ADV_MESSAGE['mess_ask_address']}],
        5: [{'text': ADV_MESSAGE['mess_ask_year']}],
        6: [{'text': ADV_MESSAGE['mess_ask_district']}],
        7: [{'text': ADV_MESSAGE['mess_ask_price']}],
        8: [{'text': ttg.text_add_foto,
            'kbd_maker': sb.farther_keyboard}],
}

step_exp_types = {
    1: ('text',),
    2: ('text',),
    3: ('text',),
    4: ('text',),
    5: ('text',),
    6: ('text',),
    7: ('text',),
    8: ('text', 'audio', 'photo', 'document', 'video', 'location'),
}
    
validators = {
    1: vlds.to_integer,
    2: vlds.to_integer,
    3: vlds.clipper,
    4: vlds.clipper,
    5: vlds.age_check,
    6: vlds.clipper,
    7: vlds.to_integer,
}