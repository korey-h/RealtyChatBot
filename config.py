BUTTONS = {
    'make_advert': 'Создать_объявление',
    'help': 'Подсказка',
    'cancel_this': 'Прекратить',
    'pass': 'Пропустить',
    'send_adv': 'Разместить',
}

MESSAGES = {
    'welcome':
        'Приветствую! Помогу оформить объявление.\n'
        'и размещу его в тематическом чате. Подробности по команде /help',
    'reg_always_on': 'Заполнение объявления уже запущено',
    'not_allowed_btn': 'Нажатая кнопка не используется '
                       'в текущем процессе',
    'mess_cancel_this': 'Команда "{}" отменена',
}

EMOJI = {'bicyclist': '\U0001F6B4', }

ADV_MESSAGE = {
    'mess_ask_space': 'Укажите общую площадь в кв. метрах '
                      '(с учётом балконов)',
    'mess_ask_flour': 'На каком этаже находится квартира?'
                      '(Для дома укажите его этажность)',
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
    'adv_confirm': 'Объявление отправлено.',
    'not_integer': 'Ожидался ввод целого числа',
    'step_is_required': 'Этот шаг нельзя пропустить',
    'pass_step': 'Этот шаг можно пропустить.',
    'mess_confirm_adv': 'Прошу подтвердить объявление:\n ',
    'mess_adv_send': 'Объявление отправлено!'
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
    'price': 'Цена, руб.'    
}


ALLOWED_BUTTONS = {
    'advert_forming': ['send_adv', 'pass']    
}
