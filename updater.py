import text_generators as ttg

from buttons import elements_butt
from config import BUTTONS, ST_TITLE
from utils import review_elem


# -------------------------------------
ELEM_GROUP_MESS = [
    {'text': 'Выберите, что нужно заменить:',
     'kbd_maker': elements_butt}]
UNO_ELEM_MESS = [review_elem, {'text': ttg.text_uno_elem}]
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
    def __init__(self, value, vtype, name, parent=None, id=None,
                 validator=None, message=None, required=None):
        self.value = value
        self.vtype = vtype
        self.parent = parent
        self.name = name        
        self.parent = parent
        self.id = id
        self.validator = validator
        self.message = message
        self.required = required

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
                 messages:dict=None):
        self.__store = {}
        self.__relations = {}
        self.__id = 0
        self.__complex_fields = {}
        if blank:
            self._make_from_blank(blank, validators, messages)

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
        if row.parent:
            row.value = None

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
                         messages:dict=None):
        for key, value in blank.items():  
            rec = Ref(blank, key)
            validator = validators.get(key) if validators else None
            message = messages.get(key) if messages else None
            if message and isinstance(value, list):
                message.extend(ELEM_GROUP_MESS)
            # elif message and isinstance(value, (int, str)):
            elif message and isinstance(value, dict):
                message.extend(UNO_ELEM_MESS)
            row = DataRow(value=rec, vtype=None, name=key, message=message,
                          validator=validator)
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

    def __group_to_table(self, parent:int, group:list):
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
                          message=UNO_ELEM_MESS)
            elem_id = self.add(row)
            ids.append(elem_id)
        return ids

    def update(self):
        for row_id, seq in self.complex_fields.items():
            groups = self.pars_by_type(seq)
            type_ids = {}
            rel = self.relations.get(row_id, [])
            for group_id in rel:
                gtype = self.get(group_id).vtype
                type_ids.update({gtype: group_id})

            for gtype, group in groups.items():
                row = DataRow(value=[], vtype=gtype, parent=row_id, name=gtype,
                              message=ELEM_GROUP_MESS)
                if type_ids.get(gtype):
                    parent = type_ids[gtype]
                    self.rep(parent, row)
                else:
                    parent = self.add(row)
                row.value = self.__group_to_table(parent=parent, group=group)


if  __name__ == '__main__':
    def set_view_attr():
        from fixtures import test_blank
        blank = test_blank()
        fot5 = {'photo': 'fotoi546uju5u56', 'caption': 'foto_5', 'content_type':'photo'}
        data_table = DataTable(blank)
        data_table.update()
        print(data_table.relations)
        print(data_table.getall()[data_table.last_id].title)
        blank['material'].append(fot5)
        blank['material'].append(fot5)
        blank['photo'].append(fot5)
        data_table.update()
        print(data_table.relations)
        print(data_table.getall()[data_table.last_id].title)
        row = data_table.get(22)
        print(data_table.get_root(row).id)


    def review_deletion():
        test_data = ['a', 'b', 'c', 'd', 'e', 'f', ['x', 'y', 'z']]
        ra = Ref(test_data, 0)
        rb = Ref(test_data, 1)
        rc = Ref(test_data, 2)
        rd = Ref(test_data, 3)
        re = Ref(test_data, 4)
        rf = Ref(test_data, 5)
        rxyz = Ref(test_data, 6)
        rx = Ref(test_data[6], 0)
        ry = Ref(test_data[6], 1)
        rz = Ref(test_data[6], 2)
        data = {
            1: DataRow(value=ra, vtype='audio', name='A', parent=8),
            2: DataRow(value=rb, vtype='audio', name='B', parent=8),
            3: DataRow(value=rc, vtype='photo', name='C', parent=9),
            4: DataRow(value=rd, vtype='photo', name='D', parent=9),
            5: DataRow(value=re, vtype='photo', name='E', parent=7),
            6: DataRow(value=rf, vtype='photo', name='F', parent=7),
            7: DataRow(value=[5, 6], vtype='photo', name='EF', parent=9),
            8: DataRow(value=[1, 2], vtype='audio', name='AB'),
            9: DataRow(value=[3, 4, 7], vtype='photo', name='CD', parent=10),
            10: DataRow(value=[9], vtype='other', name='xCD'),
            11: DataRow(value=rxyz, vtype='doc', name='xyz'),
            12: DataRow(value=rx, vtype='doc', name='x', parent=11),
            13: DataRow(value=ry, vtype='doc', name='y', parent=11),
            14: DataRow(value=rz, vtype='doc', name='z', parent=11),
        }

        relations = {
            7: [5, 6],
            8: [1, 2],
            9: [3, 4, 7],
            10: [9],
            11: [12, 13, 14]
        }

        def null(data_table:dict, id:int):
            def _null_value(id:int):
                row = data_table.get(id)
                ids = []
                if isinstance(row.value, Ref):
                    if isinstance(row.value.val, list):
                        ids = relations.get(id, []).copy()
                    else:
                        row.value.null()
                elif isinstance(row.value, list):
                    ids = row.value.copy()

                if ids:
                    for elem_id in ids:
                        _null_value(elem_id)

                if row.parent:
                    row.value = None

            def _null_relations(id:int):
                parent_id = data_table.get(id).parent
                if relations.get(id):
                    ids = relations[id].copy()
                    for elem_id in ids:
                        _null_relations(elem_id)
                if parent_id:
                    items = relations.get(parent_id)
                    items.remove(id)

            _null_value(id)
            _null_relations(id)

        null(data, 11)
        for key, row in data.items():
            print(f'{key}: {row.value}')
        print('test_data: ',test_data)
        print('ralations', relations)

    review_deletion()