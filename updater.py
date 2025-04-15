import text_generators as ttg

from buttons import elements_butt
from config import BUTTONS, ST_TITLE
from utils import review_elem


# -------------------------------------
def gen_mess_for_group(obj) -> dict:
    keyboard = elements_butt(obj)
    if not keyboard:
        return {'text': 'В этом разделе ничего нет.', 'content_type': 'text'}
    return {'text': 'Выберите, что нужно заменить:',
            'reply_markup': keyboard,
            'content_type': 'text' }

UNO_ELEM_MESS = [review_elem,
                 {'text': ttg.text_uno_elem, 'content_type': 'text'}]
# -------------------------------------


class Ref:
    def __init__(self,node, key) -> None:
        self.__node = node
        self.__key = key
    
    @property
    def val(self):
        record = self.__node[self.__key]
        if isinstance(record, list):
            return record
        elif isinstance(record, dict):
            cursor = record['content_type']
            return record[cursor]
    
    @val.setter
    def val(self, value):
        record = self.__node[self.__key]
        if isinstance(record, list):
            self.__node[self.__key] = value
        if isinstance(record, dict):
            cursor = record['content_type']
            record[cursor] = value

    @property
    def raw(self):
        return self.__node[self.__key]
    
    def update_raw(self, data: dict):
        record = self.__node[self.__key]
        if not isinstance(record, dict):
            print('Операция доступна только для значений типа Dictionary.')
            return
        if not (set(data.keys()) <= set(record.keys())):
            print('Недопустимо. Предложенные для обновления типы параметров отсутствуют в обновляемой записи.')
            return
        for key, value in data.items():
            record[key] = value

    def null(self):
        record = self.__node[self.__key]
        if isinstance(record, int):
            record = 0
        elif isinstance(record, str):
            record = '--'
        elif isinstance(record, dict):
            cursor = record['content_type']
            record[cursor] = None
        elif isinstance(record, list):
            record = [None for _ in record]
        else:
            record = None
        self.__node[self.__key] = record
    
    def __str__(self):
        record = self.__node[self.__key]
        content = str(record)
        if isinstance(record, dict):
            cursor = record['content_type']
            content = str(record[cursor])
        elif isinstance(record, list):
            content = str(record[0]) + '...'
        return 'ref:' + content


class DataRow:
    def __init__(self, value, vtype, name, parent:int=None, id:int=None,
                 validator=None, message:list=None, required:bool=None,
                 step_exp_types=[]):
        self.value = value
        self.vtype = vtype
        self.parent = parent
        self.name = name        
        self.parent = parent
        self.id = id
        self.validator = validator
        self.message = message
        self.required = required
        self.step_exp_types = step_exp_types

    @property
    def title(self, full=BUTTONS, short=ST_TITLE):
        if isinstance(self.name, int):
            if ST_TITLE.get(self.vtype):
                return ST_TITLE[self.vtype] + ' ' + str(self.name)
            return self.vtype[:3] + ' ' + str(self.name)
        else:
            if BUTTONS.get(self.name):
                return BUTTONS[self.name]
            return self.name

    def __str__(self) -> str:
        return str(self.value)

class DataTable:
    def __init__(self, blank=None, validators:dict=None,
                 messages:dict=None, expected_types:dict={}):
        self.__store = {}
        self.__relations = {}
        self.__id = 0
        self.__complex_fields = {}
        self.expected_types = expected_types
        if blank:
            self._make_from_blank(blank, validators, messages, expected_types)

    def add(self, row: DataRow) -> int:
        self.__id += 1
        self.__store[self.__id] = row
        row.id = self.__id

        if row.parent:
           group:list = self.__relations.setdefault(row.parent, [])
           group.append(self.__id)

        return self.__id
    
    def add_many(self, group:list) -> list:
        ids = []
        for row in group:
            row_id = self.add(row) 
            ids.append(row_id)
        return ids
    
    def get(self, id:int):
        return self.__store.get(id)

    def _null_relations(self, id:int):
        parent_id = self.get(id).parent
        if self.relations.get(id):
            ids = self.relations[id].copy()
            for elem_id in ids:
                self._null_relations(elem_id)
        if parent_id:
            items = self.relations.get(parent_id)
            items.remove(id)
    
    def _null_value(self, id:int):
        row =self.get(id)
        ids = []
        if isinstance(row.value, Ref):
            if isinstance(row.value.val, list):
                ids = self.relations.get(id, []).copy()
            else:
                row.value.null()
        elif isinstance(row.value, list):
            ids = row.value.copy()
        if ids:
            for elem_id in ids:
                self._null_value(elem_id)

    def null(self, id:int):
        self._null_value(id)
        self._null_relations(id)
    
    def get_root(self, node: DataRow):
        root = node
        while root.parent:
            root = self.get(root.parent)
        return root
    
    def rep(self, id:int, value):
        if isinstance(value, DataRow):
            value.id = id
        self.__store[id] = value
    
    def getall(self)-> dict:
        return self.__store
    
    def _make_from_blank(self, blank:dict, validators:dict=None,
                         messages:dict=None, expected_types:dict={}):
        for key, value in blank.items():  
            rec = Ref(blank, key)
            validator = validators.get(key) if validators else None
            step_exp_types = expected_types.get(key, {})
            message = messages.get(key) if messages else None
            if message and isinstance(value, list):
                message.append(gen_mess_for_group)
            elif message and isinstance(value, dict):
                message.extend(UNO_ELEM_MESS)
            row = DataRow(value=rec, vtype=None, name=key, message=message,
                          validator=validator, step_exp_types=step_exp_types)
            row_id = self.add(row)
            if isinstance(value, list):
                self.__complex_fields.setdefault(row_id, value)
        self.update()

    @property
    def last_id(self) -> int:
        return self.__id
    
    @property
    def relations(self) -> dict:
        return self.__relations
    
    @property
    def complex_fields(self):
        return self.__complex_fields

    def pars_by_type(self, heap: list, type_key='content_type'):
        out = {}
        for num, item in enumerate(heap):
            if item is None:
                continue
            rec = Ref(heap, num)
            group: list = out.setdefault(item[type_key], [])
            group.append(rec)
        return out

    def __group_to_table(self, parent:int, group:list, step_exp_types=[]):
        ids = []
        gtype = self.get(parent).vtype
        existents = self.relations.get(parent)
        point = 0
        num = 0
        if existents:
            point = len(existents)
            num = point
        for elem in group[point::]:
            num += 1
            row = DataRow(value=elem, vtype=gtype, parent=parent, name=num,
                          message=UNO_ELEM_MESS, step_exp_types=step_exp_types)
            elem_id = self.add(row)
            ids.append(elem_id)
        return ids

    def update(self):
        for row_id, seq in self.complex_fields.items():
            groups = self.pars_by_type(seq)
            type_ids = {}
            rel = self.relations.get(row_id, [])
            step_exp_types = self.expected_types.get(row_id)
            for group_id in rel:
                gtype = self.get(group_id).vtype
                type_ids.update({gtype: group_id})

            for gtype, group in groups.items():
                row = DataRow(value=[], vtype=gtype, parent=row_id, name=gtype,
                              message=[gen_mess_for_group],
                              step_exp_types=step_exp_types)
                if type_ids.get(gtype):
                    parent = type_ids[gtype]
                    self.rep(parent, row)
                else:
                    parent = self.add(row)
                row.value = self.__group_to_table(parent=parent, group=group,
                                                  step_exp_types=step_exp_types)
