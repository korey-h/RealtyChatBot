import models as md

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
    'foto',
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
    else:
        message = registrator.exec(data)
    print(str(message) + '-> ', end = ' ' ) 
    if not registrator.is_active:
        break
