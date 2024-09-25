MAX_IN_MEDIA = 10

BUTTONS = {
    'make_advert': 'Создать_объявление',
    'help': 'Подсказка',
    'cancel_this': 'Прекратить',
    'break': 'Завершить_все',
    'delete': 'Удалить',
    'apply': 'Применить',
    'pass': 'Пропустить',
    'redact': 'Редактировать',
    'farther': 'Далее',
    'send_adv': 'Разместить',
    'audio': 'Аудио',
    'photo': 'Фото',
    'voice': 'Голосовое',
    'video': 'Видео',
    'document': 'Документ',
    'text': 'Текст',
    'location': 'Геопозиция',
    'contact': 'Контакт',
    'sticker': 'Стикер',
    'space': 'Площадь',
    'flour': 'Этаж',
    'material': 'Материал',
    'address': 'Адрес',
    'year': 'Год',
    'district': 'Район',
    'price': 'Цена',
    'photo': 'Фото',
    'renew': 'Обновить_объявление',
}

ST_TITLE = {
    'audio': 'ауд.',
    'photo': 'фото',
    'voice': 'гол.',
    'video': 'вид.',
    'document': 'док.',
    'text': 'т.',
    'location': 'гео.',
    'contact': 'кон.',
    'sticker': 'стик.',
}

MESSAGES = {
    'welcome':
        'Приветствую! Помогу оформить объявление.\n'
        'и размещу его в тематическом чате. Подробности по команде /help',
    'reg_always_on': 'Заполнение объявления уже запущено',
    'not_allowed_btn': 'Нажатая кнопка не используется '
                       'в текущем процессе',
    'mess_cancel_this': 'Команда "{}" отменена',
    'adv_always_on': 'Процесс был запущен ранее!',
    'cancel_all': 'Все запущенные процессы прекращены.',
    'adv_search': 'Введите код для редактирования, полученный при'
                  ' отправке объявления.',
    'await_search_code': 'Ожидаю ввод кода для редактирования',              
    'cancel_other': 'Необходимо остановить другие процессы '
                    f'командой /{BUTTONS["break"]} .',
    'no_adverts': 'С введенным кодом не связано ни одно объявление!',
    'no_redact_permissions': 'У Вас нет доступа к редактированию'
                            ' этого объявления.',
}

EMOJI = {'bicyclist': '\U0001F6B4', }

ADV_MESSAGE = {
    'mess_ask_space': 'Укажите общую площадь в кв. метрах '
                      '(с учётом балконов)',
    'mess_ask_flour': 'На каком этаже находится квартира? '
                      'Для частного дома укажите его этажность.',
    'mess_ask_material': 'Из какого материала построен дом?'
                         '(панель, кирпич, монолит, дерево)',
    'mess_ask_address': 'Укажите адрес (улицу и номер дома).',
    'mess_ask_year': 'Укажите год постройки дома.',
    'mess_ask_district': 'Укажите район города (в соответствии с картой'
                         ' районов города (https://yandex.ru/maps/?um='
                         'constructor%3A6b393a25cfdeb865803754e9c7ca7a127'
                         'a0fa23aaf2c49add9e667cbfc015bf8&source='
                         'constructorLink))',
    'mess_ask_price': 'Укажите цену в рублях.',
    'mess_ask_photo': 'Вы можете добавить фотографии и описание к ним'
                      ' (через отправку сообщения).',
    'mess_change':'При помощи кнопок можно заменить ранее добавленное.',                
    'mess_farther': 'После завершения добавления нажмите кнопку '
                      f'"{BUTTONS["farther"]}".', 
    'mess_welcome_create': 'Для размещения объявления потребуется'
                            ' ответить на несколько вопросов',
    'mess_welcome_upd': 'Для редактирования информации'
                        ' нужно нажать на кнопку ниже, которая соответствует'
                        ' изменяемой части объявления',                            
    # 'adv_confirm': 'Объявление отправлено.',
    'not_integer': 'Ожидался ввод целого числа',
    'step_is_required': 'Этот шаг нельзя пропустить',
    'pass_step': 'Этот шаг можно пропустить.',
    'mess_confirm_adv': 'Прошу подтвердить объявление:\n ',
    'mess_adv_send': 'Объявление отправлено!\n'
                     ' Код для доступа к редактированию: {}',
    'non_delete': 'Удаление недоступно! Возможно только редактирование',
    'del_complete': 'Удаление выполнено.',
    'del_confirm': 'Требуется подтверждение. '
                    ' Отправьте команду на удаление еще раз',
    'wrong_year': 'Год постройки не может быть позже текущего года!',
    'rec_deleted':'Запись была удалена. Её нельзя отредактировать,'
                  ' но можно добавить новую',
    'rec_save': 'Записано.',
    'before': '>>> Было: ',
    'about_kbd': 'Также используйте команды с клавиатуры.',
    'select_del': 'Сначала выберите то, что нужно удалить.'
    }

MESS_TEMPLATES = {
    'adv_line': '{}: {}\n'
}

ADV_BLANK_WORDS = {
    'space': 'Площадь, кв.м (с учётом балконов)',
    'flour': 'Этаж (этажность)',
    'material': 'Материал дома',
    'address': 'Адрес',
    'year': 'Год постройки',
    'district': 'Район',
    'price': 'Цена, руб.',
    'photo': 'Фотографии',  
}


ALLOWED_BUTTONS = {
    'advert_forming': ['send', 'pass', 'farther', 'redact'],
    'advert_update':  ['send', 'pass', 'farther', 'update'],
}

KEYWORDS = {
    'send_btn': 'send',
    'redact_btn': 'redact',
}

KEYWORDS_MESS = {
    'button': 'Ожидаю нажатие кнопки.',
}
