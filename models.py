import base64
import datetime as dt
import hashlib

from copy import copy, deepcopy
from typing import List

import buttons as sb
import text_generators as ttg

from config import ADV_MESSAGE, KEYWORDS, KEYWORDS_MESS
from updater import DataRow, DataTable, Ref
from utils import adv_former


class RegistrProces:
    welcome_mess = [
        {'text': ADV_MESSAGE['mess_welcome_create'],
         'kbd_maker': sb.cancel_this_kbd}]
    _stop_text = 'to registration'
    _base_messages = {
        0: welcome_mess,
        1: [{'text': ADV_MESSAGE['mess_ask_space']}],
        2: [{'text': ADV_MESSAGE['mess_ask_flour']}],
        3: [{'text': ADV_MESSAGE['mess_ask_material']}],
        4: [{'text': ADV_MESSAGE['mess_ask_address']}],
        5: [{'text': ADV_MESSAGE['mess_ask_year']}],
        6: [{'text': ADV_MESSAGE['mess_ask_district']}],
        7: [{'text': ADV_MESSAGE['mess_ask_price']}],
        8: [{'text': ttg.text_add_foto,
            'kbd_maker': sb.farther_keyboard}],
        9: [{'text': ADV_MESSAGE['mess_confirm_adv'],
            'kbd_maker': sb.cancel_this_kbd},
            {'text': adv_former, 'kbd_maker': sb.send_btn}],
        10: [{'text': _stop_text}],

    }

    _step_actions = {
        0: {'name': None, 'required': True},
        1: {'name': 'space', 'required': True},
        2: {'name': 'flour', 'required': True},
        3: {'name': 'material', 'required': True},
        4: {'name': 'address', 'required': True},
        5: {'name': 'year', 'required': True},
        6: {'name': 'district', 'required': False},
        7: {'name': 'price', 'required': True},
        8: {'name': 'photo', 'required': False},
        9: {'name': None, 'required': True},
        10: {'name': None, 'required': True},
    }

    _step_keywords = {
        9: {'keyword': KEYWORDS['send_btn'], 'source': 'button'}
    }

    def __init__(self) -> None:
        self.step = 0
        self.race = None
        self.id = None
        self._finish_step = len(self._step_actions) - 1
        self.send_step = self._finish_step - 1
        self.is_active = True
        self.errors = {}
        self._fix_list = [] # сохраняет номер шага и текст ошибки

        self.adv_blank = {
            'space': None,
            'flour': None,
            'material': '',
            'address': '',
            'year': None,
            'district': '',
            'price': None,
            'photo': [],
        }
        self.title_mess_content = [
            'space', 'flour', 'material', 'address','year',
            'district','price'
        ]
        self.adv_f_send = '-'
        self.adv_blank_id = None
        self._prior_messages = deepcopy(self._base_messages)
   
    def _get_step_info(self, step: int) -> dict:
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
            9: self._check_keyword,
        }
        return validators.get(step)

    def _make_id_for_regblank(self):
        data = '.'.join([str(val) for val in self.adv_blank.values()])
        to_hash = data.encode()
        hs = hashlib.md5(to_hash).digest()
        return base64.urlsafe_b64encode(hs).decode('ascii').replace('=', '')
    
    def _pars_mess_obj(self, mess_obj) -> dict:
        def audio(mess_obj): 
            return {
                'audio': mess_obj.audio.file_id,
                'caption': mess_obj.caption}

        def photo(mess_obj):
            return {
                'photo': mess_obj.photo[-1].file_id, # выбор самого большого
                'caption': mess_obj.caption}

        def voice(mess_obj):
            return {
                'voice': mess_obj.voice.file_id,
                'caption': mess_obj.caption}

        def video(mess_obj):
            return {
                'video': mess_obj.video.file_id,
                'caption': mess_obj.caption}

        def document(mess_obj):
            return {
                'document': mess_obj.document.file_id,
                'caption': mess_obj.caption}

        def text(mess_obj):
            return {'text': mess_obj.text,}
                
    
        def location(mess_obj):
            return {
                'latitude': mess_obj.latitude,
                'longitude': mess_obj.longitude,
                'live_period': mess_obj.live_period}

        def contact(mess_obj):
            return {
                'phone_number': mess_obj.phone_number,
                'first_name': mess_obj.last_name,
                'vcard': mess_obj.vcard}

        def sticker(mess_obj):
            return {'sticker':mess_obj.sticker.file_id}

        data = {}
        con_type = mess_obj.content_type
        data['content_type'] = con_type
        datasets = {
            'audio': audio,
            'photo': photo,
            'voice': voice,
            'video': video,
            'document': document,
            'text': text,
            'location': location,
            'contact': contact,
            'sticker': sticker,       
        }
        data.update(datasets[con_type](mess_obj))
        return data

    def is_act_required(self):
        act = self._get_step_info(self.step)
        return act['required']

    def pass_step(self):
        if self.is_act_required():
            return self.mess_wrapper(ADV_MESSAGE['step_is_required'])
        act = self._get_step_info(self.step)
        entry = act['name']
        if not isinstance(self.adv_blank[entry], (list, dict)):
            self.adv_blank[entry] = {
                'content_type': 'text',
                'text': ''
            }
        self.step += 1
        return self.mess_wrapper(self.step)

    def repeat_last_step(self):
        if self.step > 0:
            self.step -= 1
        return self.exec()

    def step_handler(
            self, data, mess_obj=None, do_step_increment=True) -> List[dict]:
        pre_mess = []
        if data is not None:
            validator = self._get_validator(self.step)
            if validator:
                res = validator(data)
                if res['error']:
                    return self.mess_wrapper(res['error'])
                data = res['data']

            act = self._get_step_info(self.step)
            if act and act['name']:
                entry = act['name']
                if mess_obj: # TODO добавить возм. выбора  data, даже если есть mess_obj
                    data = self._pars_mess_obj(mess_obj)
                if isinstance(self.adv_blank[entry], list):
                    self.adv_blank[entry].append(data)
                    do_step_increment = False
                else:
                    self.adv_blank[entry] = data
        
        if self.step == 0:
            pre_mess.extend(self.mess_wrapper(self.step))

        if not do_step_increment:
            return
        elif not self._fix_list and self.step < self._finish_step:
            self.step += 1
        else:
            self.step = self._fix_list.pop()
        pre_mess.extend(self.mess_wrapper(self.step))
        return pre_mess

    def exec(self, data=None, mess_obj=None) -> dict:
        res = self.step_handler(data, mess_obj)
        if self.step == self._finish_step:
            return self.make_registration()
        return res

    def make_registration(self) -> dict:
        self.adv_blank_id = self._make_id_for_regblank()
        self.is_active = False
        mess = ADV_MESSAGE['mess_adv_send'].format(self.adv_blank_id)
        return self.mess_wrapper([
            [mess, sb.make_welcome_kbd()],
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
                if isinstance(text, (list, tuple)):
                    for elem in text:
                        pre_mess.append(elem)
                    if pre_mess[-1].get('content_type') != 'media':
                        pre_mess[-1]['reply_markup'] = keyboard
                    else:
                        pre_mess.append({'text': 'vvv', 'reply_markup': keyboard})
                else:
                    pre_mess.append({'text': text, 'reply_markup': keyboard})
            requirement = self._step_actions.get(value)
            if not requirement or not requirement['required']:
                pre_mess_1 = pre_mess.pop()
                pre_mess_2 = {
                    'text': ADV_MESSAGE['pass_step'],
                    'reply_markup': sb.pass_keyboard()
                    }
                new = sb.glue_pre_mess(pre_mess_1, pre_mess_2)
                pre_mess.append(new)
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

    def unwrapp_blank(self, blank: dict=None):
        new = {}
        blank = blank if blank else self.adv_blank
        for key, value in blank.items():
            if isinstance(value, dict):
                value = value.get('text')
            new.update({key: value})
        return new       

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
        self._to_integer(data)
        year = int(data)
        year_now = dt.datetime.now().year
        if year > year_now:
            message = ADV_MESSAGE['wrong_year']
        return {'data': data, 'error': message}
    
    def _check_keyword(self, data: str):
        message = None
        keyword = self._step_keywords.get(self.step)
        if keyword:
            if data != keyword['keyword']:
                source = keyword['source']
                message = KEYWORDS_MESS[source]
        return {'data': data, 'error': message}


class RegUpdateProces(RegistrProces):

    welcome_mess = [
        {'text': ADV_MESSAGE['mess_welcome_upd'],
         'kbd_maker': sb.welcome_upd_butt},
        {'text': ADV_MESSAGE['about_kbd'],
         'kbd_maker': sb.make_upd_kbd}]
    
    def __init__(self, blank: dict, tg_mess_ids=[]) -> None:
        super().__init__()
        validators = self._all_validators()
        messages = self._all_prior_mess()
        self.adv_blank = copy(blank)
        self.original_blank = {}
        self.butt_table = DataTable(self.adv_blank, validators, messages)
        # self._prior_messages = deepcopy(self._prior_messages)
        self._prior_messages[0] = self.welcome_mess
        self.del_is_conf = True
        self.tg_mess_ids = tg_mess_ids
    
    def mess_wrapper(self, value) -> List[dict]:
        pre_mess = []
        keyboard = None
        text = None
        if isinstance(value, str):
            pre_mess.append(
                {'text': value, 'reply_markup': keyboard}
                )  
        elif isinstance(value, (list, tuple)):
            for elem in value:
                if callable(elem):
                    pre_mess.append(elem(self))
                    continue
                elif isinstance(elem, dict):
                    text = elem['text']
                    if callable(text):
                        text = text(self)
                    maker = elem.get('kbd_maker')
                    keyboard = maker(self) if maker else None
                else:
                    text = elem
                pre_mess.append(
                    {'text': text, 'reply_markup': keyboard}
                    )
        return pre_mess                   
    
    def step_handler(self, data, mess_obj=None, ) -> List[dict]:
        pre_mess = []
        if data is None:
            if self.step == 0:
                pre_mess.extend(self.mess_wrapper(self.welcome_mess))
        elif isinstance(data, dict):
            row_id = data['pld']
            self.step = row_id
            rec = self.butt_table.get(row_id)
            if rec and rec.value is not None:
                pre_mess.extend(self.mess_wrapper(rec.message))
            else:
                pre_mess.extend(self.mess_wrapper(ADV_MESSAGE['rec_deleted']))
        else:
            row = self.butt_table.get(self.step)
            if row is None or row.value is None:
                self._set_nondeleted_step()
                row = self.butt_table.get(self.step)
            if (isinstance(row.value, Ref) and 
                    isinstance(row.value.val, (int, str))):
                validator = row.validator
                if validator:
                    res = validator(data)
                    if res['error']:
                        return self.mess_wrapper(res['error'])
                    data = res['data']                
                row.value.val = data
            
            elif (isinstance(row.value, Ref) and 
                    isinstance(row.value.val, dict) and mess_obj):
                data = self._pars_mess_obj(mess_obj)
                row.value.val = data
                  
            elif (isinstance(row.value, list) or
                    isinstance(row.value.val, list)) and mess_obj:
                data = self._pars_mess_obj(mess_obj)                
                root = self.butt_table.get_root(row)
                root.value.val.append(data)
            self.butt_table.update()
            pre_mess.extend(self.mess_wrapper(ADV_MESSAGE['rec_save']))

        return pre_mess
    
    def exec(self, data=None, mess_obj=None) -> dict:
        return self.step_handler(data, mess_obj)
    
    def _to_name_steps(self):
        named_steps = {}
        for key, data in self._step_actions.items():
            if data['name']:
                named_steps.update({data['name']: key})
        return named_steps

    def _all_validators(self):
        named_steps = self._to_name_steps()
        validators = {}
        for name, num in named_steps.items():
            validators[name] = self._get_validator(num)
        return validators
    
    def _all_prior_mess(self):
        named_steps = self._to_name_steps()
        mess = {}       
        for name, num in named_steps.items():
            mess[name] = self._prior_messages.get(num)
        return mess
    
    def _set_nondeleted_step(self, row: DataRow = None):
        if not row:
            row = self.butt_table.get(self.step)
        while row.parent and row.value is None:
            row = self.butt_table.get(row.parent)
            self.step = row.id
        return self.step
    
    def delete(self):
        if self.step == 0:
            return self.mess_wrapper(ADV_MESSAGE['select_del'])
        row = self.butt_table.get(self.step)
        if row.required:
            return self.mess_wrapper(ADV_MESSAGE['non_delete'])
        elif isinstance(row.value, list):
            if self.del_is_conf:
                self.del_is_conf = False
                return self.mess_wrapper(ADV_MESSAGE['del_confirm'])
        self.del_is_conf = True        
        self.butt_table.null(self.step)
        self._set_nondeleted_step() 
        return self.mess_wrapper(ADV_MESSAGE['del_complete'])
   
    def wrapp_blank(self):
        new = {}
        for key, value in self.adv_blank.items():
            if isinstance(value, (str, int)):
                value = {
                    'content_type': 'text',
                    'text': str(value)}
            elif isinstance(value, list):
                value = value.copy()
            new.update({key: value})
        return new             


class User:
    adv_proces_class = RegistrProces
    adv_update_class = RegUpdateProces

    def __init__(self, id, name):
        self.id = id
        self.name = name
        self._commands = []
        self.adv_proces = None
        self.upd_proces = None
        self.storage = []

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
        self.upd_proces = None

    def cmd_stack_pop(self):
        if len(self._commands) > 0:
            return self._commands.pop()
        return

    def start_advert(self):
        self.adv_proces = self.adv_proces_class()
        return
    
    def start_update(self, blank: dict, tg_mess_ids: list, adv_blank_id: str ):
        adv_blank = self.adv_proces_class().unwrapp_blank(blank)
        self.upd_proces = self.adv_update_class(adv_blank)
        self.upd_proces.adv_blank_id = adv_blank_id
        self.upd_proces.tg_mess_ids = tg_mess_ids
        self.upd_proces.original_blank = copy(adv_blank)

    def update_advert(self):
        # from fixtures import test_blank
        # blank = test_blank()
        blank = self.adv_proces.unwrapp_blank()
        self.upd_proces = self.adv_update_class(blank)
        return

    def stop_advert(self):
        self.adv_proces = None
        return

    def stop_upd(self):
        if self.adv_proces:
            self.adv_proces.adv_blank = self.upd_proces.wrapp_blank()
        self.upd_proces = None
        return
