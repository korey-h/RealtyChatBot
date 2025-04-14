import buttons as sb
import text_generators as ttg
import validators as vlds

from config import ADV_MESSAGE, ADV_BLANK_WORDS
from db_models import TitleMessages


adv_blank = {
    'space': None,
    'flour': None,
    'material': '',
    'address': '',
    'year': None,
    'district': '',
    'price': None,
    'contact': '',
    'photo': [],
}

title_mess_content = [
    'space', 'flour', 'material',
    'address','year', 'district','price', 'contact',
]

step_actions = {
        1: {'name': 'space', 'required': True},
        2: {'name': 'flour', 'required': True},
        3: {'name': 'material', 'required': True},
        4: {'name': 'address', 'required': True},
        5: {'name': 'year', 'required': True},
        6: {'name': 'district', 'required': False},
        7: {'name': 'price', 'required': True},
        8: {'name': 'contact', 'required': True},
        9: {'name': 'photo', 'required': False},
    }

step_messages = {
        1: [{'text': ADV_MESSAGE['mess_ask_space']}],
        2: [{'text': ADV_MESSAGE['mess_ask_flour']}],
        3: [{'text': ADV_MESSAGE['mess_ask_material']}],
        4: [{'text': ADV_MESSAGE['mess_ask_address']}],
        5: [{'text': ADV_MESSAGE['mess_ask_year']}],
        6: [{'text': ADV_MESSAGE['mess_ask_district']}],
        7: [{'text': ADV_MESSAGE['mess_ask_price']}],
        8: [{'text': 'Оставьте контакт для связи.'}],
        9: [{'text': ttg.text_add_foto,
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
    8: ('text',),
    9: ('text', 'audio', 'photo', 'document', 'video', 'location'),
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

#######################################################################################################
assert len(title_mess_content) > 0, "Не определены пункты бланка, входящие в основную часть объявления."

blank_keys = list(adv_blank.keys())
assert set(title_mess_content).issubset(set(blank_keys)), "В title_mess_content есть значения, отсутствующие в adv_blank."

actions_names = [step['name'] for step in step_actions.values()]
assert set(actions_names).issubset(set(blank_keys)), "В step_actions под ключами 'name' есть значения, отсутствующие в adv_blank."

assert len(blank_keys) == len(step_actions), "Не для всех пунктов бланка adv_blank определены настройки в step_actions."

step_messages_keys = list(step_messages.keys())
step_actions_keys = list(step_actions.keys())
assert set(step_messages_keys).issubset(set(step_actions_keys)), "Раличаются номера шагов (ключи) между step_messages и step_actions."
assert len(step_actions) == len(step_messages), "Не для всех пунктов бланка предусмотрены тексты сообщений-запросов."

step_exp_types_keys = list(step_exp_types.keys())
assert set(step_exp_types_keys).issubset(set(step_actions_keys)), "В step_exp_types указаны несуществующие шаги (ключи отсутствуют в step_actions)"

validating_steps = list(validators.keys())
assert set(validating_steps).issubset(set(step_actions)), "Валидаторы назначены для несуществующих шагов (ключи отсутствуют в step_actions)."

assert set(adv_blank.keys()).issubset(set(ADV_BLANK_WORDS.keys())), "Не всем ключам adv_blank присвоены имена в config.ADV_BLANK_WORDS для отображения в объявлении"

for key, item in step_exp_types.items():
    if not isinstance(item, (list, tuple)):
        text = f'Значение под ключом {key} должно быть типа списка или кортежа.'
        raise Exception(text)

if step_exp_types:
    expected_types = ('text', 'audio', 'photo', 'document', 'video', 'location')
    message_types = {}
    for key, items in step_exp_types.items():
        for type in items:
            message_types[type] = 1
    assert set(message_types.keys()).issubset(set(expected_types)), "В step_exp_types содержатся недопустимые типы сообщений."

if title_mess_content:
    out_main = []
    for key, item in adv_blank.items():
        if isinstance(item, (list, tuple)):
            continue
        if key not in title_mess_content:
            out_main.append(key)
    if out_main:
        text = ','.join(out_main)
        print('>>>\nВнимание: возможно, следующие ключи adv_blank следует включить'
              f' в title_mess_content: {text}')


if title_mess_content:
    with_wrong_types = []
    named_steps = {elem['name']:step for step, elem in step_actions.items()}
    for name in title_mess_content:
        step = named_steps[name]
        perm_types = step_exp_types.get(step)
        if perm_types:
            if len(perm_types) > 1 or (
                len(perm_types) == 1 and perm_types[0] != 'text'):
                with_wrong_types.append(str(step))
    wrongs = ','.join(with_wrong_types)
    message = 'Для корректного отображения объявления для его пунктов,'\
             ' входящих в title_mess_content, должны быть разрешены только'\
             ' сообщения только одного типа text. Следует откорректировать'\
             f' значения ключей {wrongs} в step_exp_types.'
    assert with_wrong_types == [], message

if title_mess_content:
    lost = []
    for name in title_mess_content:
        if not hasattr(TitleMessages, name):
            lost.append(name)
    wrongs = ','.join(lost)
    message = 'Для следующих ключей adv_blank должны быть добавлены одноименные '\
              f'атрибуты в модели TitleMessages: {wrongs}.\n'\
              'После добавления не забудьте создать и применить миграции для БД.'
    assert lost == [], message
