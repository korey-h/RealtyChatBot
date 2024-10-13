
from copy import deepcopy
from utils import is_sending_as_new, prepare_changed

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
            {'photo': 'photo_001'}
        ],
    }

    red_blank_equal = {
        'space': {'text': 1},
        'flour': {'text':1},
        'material': {'text':'wood'},
        'address': {'text':'street 1'},
        'year': {'text':1980},
        'district': {'text':'Oblast`'},
        'price': {'text':2000},
        'photo': [
            {'photo': 'photo_001'}
        ],
    }

    red_blank_more = {
        'space': {'text': 1},
        'flour': {'text':2},
        'material': {'text':'wood'},
        'address': {'text':'street 1'},
        'year': {'text':1980},
        'district': {'text':''},
        'price': {'text':2000},
        'photo': [
            {'photo': 'photo_001'}, {'photo': 'photo_002'}, {'photo': 'photo_003'}
        ],
    }

    red_blank_mini = {
        'space': {'text': 1},
        'flour': {'text':1},
        'material': {'text':'wood'},
        'address': {'text':'street 1'},
        'year': {'text':1980},
        'district': {'text':'Oblast`'},
        'price': {'text':2000},
        'photo': [],
    }

    title_mess_content = ['space', 'flour', 'material', 'address','year',
                'district','price']
    tg_mess_ids = ['00000', '00011']
    res = prepare_changed(original_blank, red_blank_mini, title_mess_content, tg_mess_ids)       
    print(res)

    title_mess_content = ['space', 'material', 'address','year',
                'district','price']
    tg_mess_ids = ['00000', '00011', '00020']
    res = prepare_changed(original_blank, red_blank_mini, title_mess_content, tg_mess_ids)       
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

if __name__ == '__main__':
    test_is_sending_as_new()