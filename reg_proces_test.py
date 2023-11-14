import models as md


class Photo():
    def __init__(self, file_id: str) -> None:
        self.file_id = file_id

    def __str__(self) -> str:
        return  self.file_id


class SimplMessage():
    def __init__(self, mess_type: str, photo: Photo=None, caption=None) -> None:
        self.content_type = mess_type
        self.photo =  [photo, ]
        self.caption = caption
    
    def to_dict(self):
        return {
            'photo': self.photo,
            'caption': self.caption,
            'content_type': self.content_type
        }
    
    def __str__(self) -> str:
        return 'c: ' + self.caption

f1 = Photo('http://t.me/1')
f2 = Photo('http://t.me/2')

foto1 = SimplMessage('photo', f1, 'первая фотка')
foto2 = SimplMessage('photo', f2, 'ффторая ')


scena = [
    '60',
    '1',
    'кирпич',
    None,
    'Big авеню',
    None,
    '1980',
    'район',
    '10000',
    foto1,
    foto2,
    None,
    'sen',
    'send'

]

registrator = md.RegistrProces()

message = registrator.exec('race_id')
print(str(message) + '-> ', end = ' ' )
for data in scena:
    print (str(data))
    if data is None:
        message = registrator.pass_step()
    elif data == 'repeat':
        message = registrator.repeat_last_step()
    elif isinstance(data, SimplMessage):
        message = registrator.exec('dict', data)
    else:
        message = registrator.exec(data)
    print(str(message) + '-> ', end = ' ' ) 
    if not registrator.is_active:
        break
