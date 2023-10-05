import base64
import hashlib

from typing import List

import buttons as sb

from config import ADV_MESSAGE
from utils import adv_sender


class RegistrProces:

    def __init__(self) -> None:
        self.step = 0
        self.race = None
        self.id = None
        self.is_active = True
        self.errors = {}
        self._fix_list = []
        self.adv_sender = adv_sender
        self.adv_blank = {
            'space': None,
            'flour': None,
            'material': '',
            'address': '',
            'year': None,
            'district': '',
            'price': None
        }
        self.adv_blank_id = None

    _stop_text = 'to registration'
    _finish_step = 8
    _prior_messages = {
        1: [{'text': ADV_MESSAGE['mess_ask_space'],
            'kbd_maker': sb.cancel_this_kbd}],
        2: [{'text': ADV_MESSAGE['mess_ask_flour'],
            'kbd_maker': sb.cancel_this_kbd}],
        3: [{'text': ADV_MESSAGE['mess_ask_material']}],
        4: [{'text': ADV_MESSAGE['mess_ask_address']}],
        5: [{'text': ADV_MESSAGE['mess_ask_year']}],
        6: [{'text': ADV_MESSAGE['mess_ask_district']}],
        7: [{'text': ADV_MESSAGE['mess_ask_price']}],
        8: [{'text': _stop_text}],

    }

    _step_actions = {
        1: {'name': 'space', 'required': True},
        2: {'name': 'flour', 'required': True},
        3: {'name': 'material', 'required': True},
        4: {'name': 'address', 'required': True},
        5: {'name': 'year', 'required': True},
        6: {'name': 'district', 'required': True},
        7: {'name': 'price', 'required': True},
        8: {'name': 'registration', 'required': True},
    }

    def _get_action(self, step: int) -> dict:
        return self._step_actions.get(step)

    def _get_step_names(self) -> dict:
        return {
            val['name']: st for st, val in self._step_actions.items()
        }

    def _get_validator(self, step: int):
        validators = {
            1: self._to_integer,
            2: self._to_integer,
            3: self._clipper,
            4: self._clipper,
            5: self._age_check,
            6: self._clipper,
            7: self._to_integer,
        }
        return validators.get(step)

    def _make_id_for_regblank(self):
        data = '.'.join([str(val) for val in self.adv_blank.values()])
        to_hash = data.encode()
        hs = hashlib.md5(to_hash).digest()
        return base64.urlsafe_b64encode(hs).decode('ascii').replace('=', '')

    def is_act_required(self):
        act = self._get_action(self.step)
        return act['required']

    def pass_step(self):
        if self.is_act_required():
            return self.mess_wrapper(ADV_MESSAGE['step_is_required'])
        self.step += 1
        return self.mess_wrapper(self.step)

    def repeat_last_step(self):
        if self.step > 0:
            self.step -= 1
        return self.exec()

    def step_handler(self, data) -> dict:
        if data is not None:
            validator = self._get_validator(self.step)
            if validator:
                res = validator(data)
                if res['error']:
                    return self.mess_wrapper(res['error'])
                data = res['data']

            act = self._get_action(self.step)
            if act:
                entry = act['name']
                self.adv_blank[entry] = data

        if not self._fix_list and self.step < self._finish_step:
            self.step += 1
        else:
            self.step = self._fix_list.pop()
        return self.mess_wrapper(self.step)

    def exec(self, data=None) -> dict:
        res = self.step_handler(data)
        if self.step == self._finish_step:
            return self.make_registration()
        return res

    def make_registration(self) -> dict:
        self.adv_blank_id = self._make_id_for_regblank()
        text = adv_sender(self.adv_blank)['text']
        # # keyboard = sb.adv_update_button(self)
        self.is_active = False
        return self.mess_wrapper([
            [text, sb.make_welcome_kbd()],
            ])

    def mess_wrapper(self, value) -> List[dict]:
        keyboard = None
        text = None
        if isinstance(value, str):
            text = value
        elif isinstance(value, int):
            pre_mess = []
            datas = self._prior_messages[value]
            for data in datas:
                text = data['text']
                if callable(text):
                    text = text(self)
                maker = data.get('kbd_maker')
                keyboard = maker(self) if maker else None
                pre_mess.append({'text': text, 'reply_markup': keyboard})
            return pre_mess
        elif isinstance(value, (list, tuple)):
            pre_mess = []
            for data in value:
                text = data[0]
                keyboard = data[1]
                pre_mess.append({'text': text, 'reply_markup': keyboard})
            return pre_mess
        elif isinstance(value, dict):
            return [value]
        return [{'text': text, 'reply_markup': keyboard}]

    def _clipper(self, data: str) -> dict:
        data = data.strip()
        return {'data': data, 'error': None}

    def _to_integer(self, data: str) -> dict:
        message = None
        try:
            data = int(data)
        except Exception:
            data = None
            message = ADV_MESSAGE['not_integer']
        return {'data': data, 'error': message}

    def _age_check(self, data: str):
        message = None
        return {'data': data, 'error': message}


class RegUpdateProces(RegistrProces):
    pass


class User:
    adv_proces_class = RegistrProces
    adv_update_class = RegUpdateProces

    def __init__(self, id):
        self.id = id
        self._commands = []
        self.adv_proces = None

    def is_stack_empty(self):
        return len(self._commands) == 0

    def get_cmd_stack(self):
        if len(self._commands) > 0:
            return self._commands[-1]
        return []

    def set_cmd_stack(self, cmd_stack):
        if isinstance(cmd_stack, dict):
            self._commands.append(cmd_stack)
        else:
            keys = ('cmd_name', 'cmd', 'data', 'called_by')
            if isinstance(cmd_stack, (list, tuple)):
                s = tuple(cmd_stack)
                keys_am = len(keys)
                values = s[:keys_am] if len(s) >= keys_am else (
                    s + tuple({} for _ in range(keys_am - len(s)))
                    )
            else:
                values = (cmd_stack, cmd_stack, {}, None)
            self._commands.append(
                {key: val for key, val in zip(keys, values)}
            )

    cmd_stack = property(get_cmd_stack, set_cmd_stack)

    def clear_stack(self):
        self._commands.clear()

    def cancel_all(self):
        self.clear_stack()
        self.adv_proces = None

    def cmd_stack_pop(self):
        if len(self._commands) > 0:
            if self.adv_proces:
                self.stop_registration()
            return self._commands.pop()
        return None

    def start_advert(self):
        self.adv_proces = self.adv_proces_class()
        return None

    def update_advert(self):
        self.adv_proces = self.adv_update_class()
        return None

    def stop_advert(self):
        self.adv_proces = None
        return None
