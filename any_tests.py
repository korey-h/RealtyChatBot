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

if __name__ == '__main__':
    # test_is_sending_as_new()
    # test_prepare_changed()
    test_sending_block()
    # test_make_title()
    # test_sending_text_block()
