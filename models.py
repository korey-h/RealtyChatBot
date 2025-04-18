import base64
import json
import hashlib

from copy import copy, deepcopy
from typing import List

import blank_config as bc
import buttons as sb
import text_generators as ttg
import validators as vlds

from config import ADV_MESSAGE, KEYWORDS, KEYWORDS_MESS
from updater import DataRow, DataTable, Ref
from utils import adv_former, SendingBlock


class RegistrProces:
    welcome_mess = [
        {'text': ADV_MESSAGE['mess_welcome_create'],
         'kbd_maker': sb.cancel_this_kbd}]
    _stop_text = 'to registration'

    _step_keywords = {
        9: {'keyword': KEYWORDS['send_btn'], 'source': 'button'}
    }
    
    def __init__(self) -> None:
        self.step = 0
        self.race = None
        self.id = None
        self._finish_step = len(bc.step_actions) + 2
        self.send_step = self._finish_step - 1
        self.is_active = True
        self.errors = {}
        self._fix_list = [] # сохраняет номер шага и текст ошибки

        self.adv_blank = bc.adv_blank
        self.title_mess_content = bc.title_mess_content
        self.adv_f_send = '-'
        self.adv_blank_id = None
        self.adv_serial_num = None

        self._step_actions = {0: {'name': None, 'required': True}, }
        self._step_actions.update(bc.step_actions)
        self._step_actions.update({
            self.send_step: {'name': None, 'required': True},
            self._finish_step: {'name': None, 'required': True},
        })

        self._base_messages = {
            0: self.welcome_mess,
            self.send_step: [{'text': ADV_MESSAGE['mess_confirm_adv'],
                             'kbd_maker': sb.cancel_this_kbd},
                             {'text': adv_former, 'kbd_maker': sb.send_btn}],
            self._finish_step: [{'text': self._stop_text}],
        }
        self._base_messages.update(bc.step_messages)
        self._prior_messages = deepcopy(self._base_messages)
    
        self.validators = {self.send_step: vlds.check_keyword}
        self.validators.update(bc.validators)
        self._step_exp_types = bc.step_exp_types
   
    def step_exp_types(self, step: int=None):
        if step is None:
            return self._step_exp_types.get(self.step)
        return self._step_exp_types.get(step)

    def _get_step_info(self, step: int) -> dict:
        return self._step_actions.get(step)

    def _get_step_names(self) -> dict:
        return {
            val['name']: st for st, val in self._step_actions.items()
        }

    def _get_validator(self, step: int):
        return self.validators.get(step)

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
            parsed = {
                'latitude': mess_obj.location.latitude,
                'longitude': mess_obj.location.longitude,
                'live_period': 2147483647} # для возможности редактирования
            serialised = json.dumps(parsed)
            parsed['location'] = serialised
            return parsed

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
                res = validator(self, data)
                if res['error']:
                    return self.mess_wrapper(res['error'])
                data = res['data']

            act = self._get_step_info(self.step)
            if act and act['name']:
                entry = act['name']
                if mess_obj:
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
        elif self._fix_list:
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
        return [{'text': 'finish'}]
    
    @property
    def finish_message(self):
        mess = ADV_MESSAGE['mess_adv_send'].format(self.adv_serial_num, self.adv_blank_id)
        return self.mess_wrapper([
            [mess, sb.make_welcome_kbd()],
            [ADV_MESSAGE['mess_adv_send_p2'], sb.renew_btn(self.adv_blank_id)],
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
                    pre_mess.extend(text)
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
                if isinstance(data, SendingBlock):
                    pre_mess.append(data)
                    continue
                text = data[0]
                keyboard = data[1]
                pre_mess.append({'text': text, 'reply_markup': keyboard})
            return pre_mess

        elif isinstance(value, dict):
            return [value]
        return [{'text': text, 'reply_markup': keyboard}]

  
        message = None
        keyword = self._step_keywords.get(self.step)
        if keyword:
            if data != keyword['keyword']:
                source = keyword['source']
                message = KEYWORDS_MESS[source]
        return {'data': data, 'error': message}


class RegUpdateProces(RegistrProces):

    welcome_mess = [
        {'text': ttg.text_welcome_upd_mess,
         'kbd_maker': sb.welcome_upd_butt},
        {'text': ADV_MESSAGE['about_kbd'],
         'kbd_maker': sb.make_upd_kbd}]
    
    def __init__(self, blank: dict, tg_mess_ids=[]) -> None:
        super().__init__()
        validators = self._all_validators()
        messages = self._all_prior_mess()
        self.adv_blank = copy(blank) # TODO проверить необходимость deepcopy
        self.original_blank = {}
        self.butt_table = DataTable(self.adv_blank, validators, messages,
                                    self._exp_types_f_names())
        self._prior_messages[0] = self.welcome_mess
        self.del_is_conf = True
        self.tg_mess_ids = tg_mess_ids
        self.db_mess_objs = {}
    
    def step_exp_types(self, step: int=None):
        if step is None:
            row = self.butt_table.get(self.step)
        else:
            row = self.butt_table.get(step)
        if not row:
            return []
        return row.step_exp_types
 
    def _exp_types_f_names(self):
        new = {}
        for step, types in self._step_exp_types.items():
            name = self._step_actions[step]['name']
            if not name:
                continue
            new[name] = types
        return new

    def mess_wrapper(self, value) -> List[dict]:
        pre_mess = []
        keyboard = None
        text = None

        def _prepare_text(mess: dict):
            text = mess.get('text')
            if not text:
                return (mess)
            if callable(text):
                text = text(self)
            
            keyboard = mess.get('reply_markup')
            if not keyboard:
                maker = mess.get('kbd_maker')
                keyboard = maker(self) if maker else None
            return {'text': text, 'reply_markup': keyboard}

        if isinstance(value, str):
            pre_mess.append({'text': value, 'reply_markup': keyboard})
        elif isinstance(value, dict):
            pre_mess.append(_prepare_text(elem))
        elif isinstance(value, (list, tuple)):
            for elem in value:
                if callable(elem):
                    generated_pre_mess = elem(self)
                    if not generated_pre_mess:
                        continue
                    pre_mess.append(generated_pre_mess)
                elif isinstance(elem, dict):
                    pre_mess.append(_prepare_text(elem))
                elif isinstance(elem, (list, tuple)):
                    text = elem[0]
                    keyboard = elem[1]
                    pre_mess.append({'text': text, 'reply_markup': keyboard})
                else:
                    text = elem
                    pre_mess.append({'text': text, 'reply_markup': keyboard})
        return pre_mess                   
    
    def step_handler(self, data, mess_obj ) -> List[dict]:
        pre_mess = []
        if data is None:
            if self.step == 0:
                pre_mess.extend(self.mess_wrapper(self.welcome_mess))
        elif isinstance(data, dict):
            row_id = data['pld']
            self.step = row_id
            rec = self.butt_table.get(row_id)
            if rec and rec.value:
                pre_mess.extend(self.mess_wrapper(rec.message))
            else:
                pre_mess.extend(self.mess_wrapper(ADV_MESSAGE['rec_deleted']))
        elif self.step == 0:
            warning = {'text': ADV_MESSAGE['mess_select_button']}
            pre_mess.append(warning)
        else:
            row = self.butt_table.get(self.step)
            if row is None or row.value is None:
                self._set_nondeleted_step()
                row = self.butt_table.get(self.step)
            if (isinstance(row.value, Ref) and 
                    isinstance(row.value.val, (int, str))):
                if row.value.raw['content_type'] == 'text':
                    validator = row.validator
                    if validator:
                        res = validator(self, data)
                        if res['error']:
                            return self.mess_wrapper(res['error'])
                        else:
                            data = res['data']
                    row.value.val = data
                else:
                    data = self._pars_mess_obj(mess_obj)
                    row.value.update_raw(data)
                  
            elif (isinstance(row.value, list) or 
                    isinstance(row.value.val, list)):
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
        elif isinstance(row.value, list) or isinstance(row.value.val, list):
            if self.del_is_conf:
                self.del_is_conf = False
                return self.mess_wrapper(ADV_MESSAGE['del_confirm'])
        self.del_is_conf = True        
        self.butt_table.null(self.step)
        self._set_nondeleted_step() 
        return self.mess_wrapper(ADV_MESSAGE['del_complete'])


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
    
    def start_update(self, adv_blank: dict, adv_blank_id: str,
                     db_mess_objs: dict ):
        self.upd_proces = self.adv_update_class(adv_blank)
        self.upd_proces.adv_blank_id = adv_blank_id
        self.upd_proces.original_blank = deepcopy(adv_blank)
        self.upd_proces.db_mess_objs = db_mess_objs

    def update_advert(self):
        self.upd_proces = self.adv_update_class(self.adv_proces.adv_blank)
        return

    def stop_advert(self):
        self.adv_proces = None
        return

    def stop_upd(self):
        if self.adv_proces:
            self.adv_proces.adv_blank = self.upd_proces.adv_blank
        self.upd_proces = None
        return
