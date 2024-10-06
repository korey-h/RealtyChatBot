from utils import find_changes


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

# title_mess_content = ['space', 'material', 'address','year',
#             'district','price']
# tg_mess_ids = ['00000', '00011', '00020']


res = find_changes(original_blank, red_blank_mini, title_mess_content, tg_mess_ids)


print(res)
