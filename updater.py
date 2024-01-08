from config import BUTTONS, ST_TITLE


class Ref:
    def __init__(self,node, key) -> None:
        self.__node = node
        self.__key = key
    
    @property
    def val(self):
        return self.__node[self.__key]
    
    @val.setter
    def val(self, value):
        self.__node[self.__key] = value
    
    def __str__(self):
        return 'ref:' + str(self.__node[self.__key])


class DataRow:
    def __init__(self, value, vtype, name, parent=None, id=None,
                 validator=None, message=None ):
        self.value = value
        self.vtype = vtype
        self.parent = parent
        self.name = name        
        self.parent = parent
        self.id = id
        self.validator = validator
        self.message = message

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
    
    def get_root(self, node: DataRow):
        root = node
        while root.parent:
            root = self.get(root.parent)
        return root
    
    def rep(self, id:int, value):
        self.__store[id] = value
    
    def getall(self)-> dict:
        return self.__store
    
    def _make_from_blank(self, blank:dict, validators:dict=None,
                         messages:dict=None):
        for key, value in blank.items():  
            rec = Ref(blank, key)
            validator = validators.get(key) if validators else None
            message = messages.get(key) if messages else None
            row = DataRow(value=rec, vtype=None, name=key, message=message,
                          validator=validator)
            row_id = self.add(row)
            if isinstance(value, list):
                self.__complex_fields.setdefault(row_id, value)

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
            rec = Ref(heap, num)
            group: list = out.setdefault(item[type_key], [])
            group.append(rec)
        return out

    def __group_to_table(self, parent:int, group:list):
        gtype = self.get(parent).vtype
        existents = self.relations.get(parent)
        point = 0
        num = 1
        if existents:
            point = len(existents)
            num = point + 1
        for elem in group[point::]:
            row = DataRow(value=elem, vtype=gtype, parent=parent, name=num)
            self.add(row)

    def update(self): 
        for key, seq in self.complex_fields.items():
            groups = self.pars_by_type(seq)
            type_ids = {}
            rel = self.relations.get(key)
            if rel:
                for group_id in rel:
                    gtype = self.get(group_id).vtype
                    type_ids.update({gtype: group_id})

            for gtype, group in groups.items():
                row = DataRow(value=group, vtype=gtype, parent=key, name=gtype)
                if type_ids.get(gtype):
                    parent = type_ids[gtype]
                    self.rep(parent, row)
                else:
                    parent = data_table.add(row)
                self.__group_to_table(parent=parent, group=group)


if  __name__ == '__main__':
    from fixtures import test_blank
    blank = test_blank()
    fot5 = {'photo': 'fotoi546uju5u56', 'caption': 'foto_5', 'content_type':'photo'}
    data_table = DataTable(blank)
    data_table.update()
    print(data_table.relations)
    print(data_table.getall()[data_table.last_id].title)
    blank['about'].append(fot5)
    blank['about'].append(fot5)
    blank['photo'].append(fot5)
    data_table.update()
    print(data_table.relations)
    print(data_table.getall()[data_table.last_id].title)
    row = data_table.get(22)
    print(data_table.get_root(row).id)