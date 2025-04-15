import pprint

from copy import deepcopy
from models import RegistrProces
from utils import is_sending_as_new, make_title_f_blank, prepare_changed, SendingBlock

def test_prepare_changed():
    original_blank = {
        'space': {'content_type': 'text', 'text': 1, 'tg_mess_id': '00001'},
        'flour': {'content_type': 'text', 'text':2, 'tg_mess_id': '00001'},
        'material': {'content_type': 'text', 'text':'wood', 'tg_mess_id': '00001'},
        'address': {'content_type': 'text', 'text':'street 1', 'tg_mess_id': '00001'},
        'year': {'content_type': 'text', 'text':1980, 'tg_mess_id': '00001'},
        'district': {'content_type': 'text', 'text':'', 'tg_mess_id': '00001'},
        'price': {'content_type': 'text', 'text':2000, 'tg_mess_id': '00001'},
        'photo': [
            {'content_type': 'photo', 'photo': 'photo_001', 'tg_mess_id': '00011', 'db_id': 1},
            {'content_type': 'photo', 'photo': 'photo_002', 'tg_mess_id': '00012', 'db_id': 2},
            {'content_type': 'document', 'document': 'doc_001', 'tg_mess_id': '00021', 'db_id': 3},
            {'content_type': 'document', 'document': 'doc_002', 'tg_mess_id': '00022', 'db_id': 4},
        ],
    }

    red_blank_equal = deepcopy(original_blank)

    red_blank_del = deepcopy(original_blank)
    red_blank_del['photo'][1] = {'content_type': 'photo', 'photo': None, 'tg_mess_id': '00012', 'db_id': 2}


    red_blank_add_del = deepcopy(original_blank)
    red_blank_add_del['photo'][1] = {'content_type': 'photo', 'photo': None, 'tg_mess_id': '00012', 'db_id': 2}
    red_blank_add_del['photo'].append(
        {'content_type': 'photo', 'photo': 'photo_003'}
        )

    title_mess_content = ['space', 'flour', 'material', 'address','year',
                'district','price']
    tg_mess_ids = ['00000', '00011']

    res = prepare_changed(original_blank, red_blank_equal, title_mess_content, tg_mess_ids)       
    print('>>>\n',res)

    res = prepare_changed(original_blank, red_blank_del, title_mess_content, tg_mess_ids)       
    print('>>>\n',res)

    res = prepare_changed(original_blank, red_blank_add_del, title_mess_content, tg_mess_ids)       
    print('>>>\n',res)

    # title_mess_content = ['space', 'material', 'address','year',
    #             'district','price']
    red_blank_flour = deepcopy(original_blank)
    red_blank_flour['flour']['text'] = 3
    res = prepare_changed(original_blank, red_blank_flour, title_mess_content, tg_mess_ids)       
    print('>>>\n',res)


def test_is_sending_as_new():
    title_mess_content = ['space', 'flour', 'material', 'address','year',
                'district','price']
    original_blank = {
        'space': {'content_type': 'text', 'text': 1},
        'flour': {'content_type': 'text', 'text':2},
        'material': {'content_type': 'text', 'text':'wood'},
        'address': {'content_type': 'text', 'text':'street 1'},
        'year': {'content_type': 'text', 'text':1980},
        'district': {'content_type': 'text', 'text':''},
        'price': {'content_type': 'text', 'text':2000},
        'photo': [
            {'content_type': 'photo', 'photo': 'photo_001'},
            {'content_type': 'photo', 'photo': 'photo_002'},
            {'content_type': 'document', 'document': 'doc_001'},
            {'content_type': 'document', 'document': 'doc_002'},
        ],
    }

    blank_add_photo = deepcopy(original_blank)
    blank_add_photo['photo'].append(
        {'content_type': 'photo', 'photo': 'photo_003'},
    )
    blank_add_type = deepcopy(original_blank)
    blank_add_type['photo'].append(
        {'content_type': 'audio', 'audio': 'au_001'},
    )
    blank_del_doc = deepcopy(original_blank)
    blank_del_doc['photo'].pop(3)

    blank_del_add = deepcopy(original_blank)
    blank_del_add['photo'][1] =  {'content_type': 'document', 'document': 'doc_003'}

    blank_del_add_photo = deepcopy(original_blank)
    blank_del_add_photo['photo'][1] = {'content_type': 'photo', 'photo': None}
    blank_del_add_photo['photo'].append({'content_type': 'photo', 'photo': 'photo_200'})

    res1 = is_sending_as_new(original_blank, blank_add_photo, 
                              title_mess_content)
    res2 = is_sending_as_new(original_blank, blank_add_type, 
                              title_mess_content)
    res3 = is_sending_as_new(original_blank, blank_del_doc, 
                              title_mess_content)
    res4 = is_sending_as_new(original_blank, blank_del_add, 
                              title_mess_content)
    res5 = is_sending_as_new(original_blank, blank_del_add_photo, 
                              title_mess_content)
    print(res1, res2, res3, res4, res5)


def test_sending_block():
    MAX_IN_MEDIA = 3
    photo_group = [
        {'content_type': 'photo', 'photo': 'photo_001', 'enclosure_num': 1,},
        {'content_type': 'photo', 'photo': 'photo_005', 'enclosure_num': 5,},
        {'content_type': 'photo', 'photo': 'photo_002', 'enclosure_num': 2,},
        {'content_type': 'photo', 'photo': 'photo_004', 'enclosure_num': 4,},
        {'content_type': 'photo', 'photo': 'photo_006',},
        {'content_type': 'photo', 'photo': 'photo_007',},
        ]

    titles = {
        'photo': {'content_type': 'text', 'text': 'Заголовок фото', 'enclosure_num':0, 'sequence_num':1}
    }

    photo_block = SendingBlock(items=photo_group,blank_line_name='photo', group_num=0, 
                 group_type='photo',)
    # photo_block.find_set_title(titles)
    photo_block.max_media = MAX_IN_MEDIA
    print('\n')
    # pprint.pprint(photo_block.get_formated())
    pprint.pprint(photo_block.get_for_sending())

def test_sending_text_block():
    MAX_TEXT = 20
    text_group = [
        {'content_type': 'text', 'text': '123456789-10-11-12-13-14-15', 'enclosure_num': 1,},
        {'content_type': 'text', 'text': 'text_006',},
        {'content_type': 'text', 'text': 'text_007',},
        ]

    titles = {
        'text': {'content_type': 'text', 'text': 'Заголовок фото', 'enclosure_num':0, 'sequence_num':1}
    }

    text_block = SendingBlock(items=text_group,blank_line_name='text', group_num=0, 
                 group_type='text', max_len_text=MAX_TEXT)
    pprint.pprint(text_block.items)


def test_make_title():
    reg_proces = RegistrProces()
    title = make_title_f_blank(reg_proces)
    out = title.get_for_sending()
    pprint.pprint(out)


def test_inspect():
    import inspect

    import time

    def some_func(run, stop, date, time, ):
        pass

    start = time.time()
    for i in range(0,1000):
        args = inspect.getfullargspec(some_func).args
    print(time.time()-start)
    print("Аргументы функции:", args)


def test_sorting_mess():
    group_0 = [(0,0), (0,2), (0,1)]
    group_1 = [(1,1), (1,3), (1,2), (1,0)]
    group_2 = [(2,0), (2,1), ]
    row = group_2 + group_0 + group_1
    row.sort(key=lambda elem: str(elem[0])+str(elem[1]))
    print(row)


def test_updater():
    from updater import DataRow, DataTable, Ref
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



if __name__ == '__main__':
    # test_is_sending_as_new()
    # test_prepare_changed()
    test_sending_block()
    # test_make_title()
    # test_sending_text_block()


