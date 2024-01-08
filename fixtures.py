def test_blank():
    blank = {
        'space': 160,
        'flour': 6,
        'about': [],
        'district': 'Defaulty',
        'price': 10000,
        'photo': [],
        'nano': '',
        'pano': '',
        }

    au1 = {'audio': 'a5+5+65+5+565', 'caption': 'au1', 'content_type':'audio'}
    au2 = {'audio': 'a6+5+65+5+565', 'caption': 'au2', 'content_type':'audio'}
    au3 = {'audio': 'a7+5+65+5+565', 'caption': 'au3', 'content_type':'audio'}
    au4 = {'audio': 'a8+5+65+5+565', 'caption': 'au4', 'content_type':'audio'}

    fot1 = {'photo': 'fnji546uju5u55', 'caption': 'foto_1', 'content_type':'photo'}
    fot2 = {'photo': 'f2ji546uju5u55', 'caption': 'foto_2', 'content_type':'photo'}
    fot3 = {'photo': 'f3ji546uju5u55', 'caption': 'foto_3', 'content_type':'photo'}
    fot4 = {'photo': 'f4ji546uju5u55', 'caption': 'foto_4', 'content_type':'photo'}
    fot5 = {'photo': 'fotoi546uju5u56', 'caption': 'foto_5', 'content_type':'photo'}

    doc1 = {'document': 'doc__146uju5u55', 'caption': 'doc_1', 'content_type':'document'}
    doc2 = {'document': 'doc__146uju5u55', 'caption': 'doc_2', 'content_type':'document'}
    doc3 = {'document': 'doc__146uju5u55', 'caption': 'doc_3', 'content_type':'document'}
    doc4 = {'document': 'doc__146uju5u55', 'caption': 'doc_4', 'content_type':'document'}

    blank['about'] = [doc1, fot4, doc2, doc3, doc4]
    blank['photo'] = [fot1, fot2, au1, au2, fot3, au3, au4]
    return blank