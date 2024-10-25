import pprint

from copy import deepcopy
from utils import is_sending_as_new, prepare_changed, SendingBlock

def test_prepare_changed():
    original_blank = {
        'space': {'text': 1},
        'flour': {'text':2},
        'material': {'text':'wood'},
        'address': {'text':'street 1'},
        'year': {'text':1980},
        'district': {'text':''},
        'price': {'text':2000},
        'photo': [
            {'photo': 'photo_001', 'tg_mess_id': '00011'}
        ],
    }

    red_blank_equal = deepcopy(original_blank)

    red_blank_more = deepcopy(original_blank)
    red_blank_more['photo'].extend([
        {'photo': 'photo_002', 'tg_mess_id': None},
        {'photo': 'photo_003', 'tg_mess_id': None}])


    red_blank_mini = deepcopy(original_blank)
    red_blank_mini['photo'] = []

    title_mess_content = ['space', 'flour', 'material', 'address','year',
                'district','price']
    tg_mess_ids = ['00000', '00011']

    res = prepare_changed(original_blank, red_blank_equal, title_mess_content, tg_mess_ids)       
    print(res)

    res = prepare_changed(original_blank, red_blank_more, title_mess_content, tg_mess_ids)       
    print(res)

    res = prepare_changed(original_blank, red_blank_mini, title_mess_content, tg_mess_ids)       
    print(res)

    title_mess_content = ['space', 'material', 'address','year',
                'district','price']
    original_blank['flour'].update({'tg_mess_id': '00001'})
    red_blank_flour = deepcopy(original_blank)
    red_blank_flour['flour']['text'] = 3
    res = prepare_changed(original_blank, red_blank_flour, title_mess_content, tg_mess_ids)       
    print(res)


def test_is_sending_as_new():
    title_mess_content = ['space', 'flour', 'material', 'address','year',
                'district','price']
    original_blank = {
        'space': {'text': 1},
        'flour': {'text':2},
        'material': {'text':'wood'},
        'address': {'text':'street 1'},
        'year': {'text':1980},
        'district': {'text':''},
        'price': {'text':2000},
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
    res1 = is_sending_as_new(original_blank, blank_add_photo, 
                              title_mess_content)
    res2 = is_sending_as_new(original_blank, blank_add_type, 
                              title_mess_content)
    res3 = is_sending_as_new(original_blank, blank_del_doc, 
                              title_mess_content)
    res4 = is_sending_as_new(original_blank, blank_del_add, 
                              title_mess_content)
    print(res1, res2, res3, res4)


def test_sending_block():

    photo_group = [
        {'content_type': 'photo', 'photo': 'photo_001', 'enclosure_num': 1,},
        {'content_type': 'photo', 'photo': 'photo_004', 'enclosure_num': 4,},
        # {'content_type': 'photo', 'photo': 'photo_002', 'enclosure_num': 2,},
        # {'content_type': 'photo', 'photo': 'photo_005', 'enclosure_num': 5,},
        # {'content_type': 'photo', 'photo': 'photo_006',},
        {'content_type': 'photo', 'photo': 'photo_007',},
        ]

    titles = {
        4: {'content_type': 'text', 'text': 'Заголовок фото', 'enclosure_num':0, 'sequence_num':1}
    }

    photo_block = SendingBlock(photo_group, 1, 'foto')
    photo_block.find_set_title(titles)
    pprint.pprint(photo_block.get_formated())

if __name__ == '__main__':
    # test_is_sending_as_new()
    # test_prepare_changed()
    test_sending_block()