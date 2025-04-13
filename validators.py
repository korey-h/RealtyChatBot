import datetime as dt

from config import ADV_MESSAGE, KEYWORDS_MESS


def clipper(obj, data: str) -> dict:
    data = data.strip()
    return {'data': data, 'error': None}


def to_integer(obj, data: str) -> dict:
    message = None
    try:
        data = int(data)
    except Exception:
        data = None
        message = ADV_MESSAGE['not_integer']
    return {'data': data, 'error': message}


def age_check(obj, data: str):
    message = None
    to_integer(obj, data)
    year = int(data)
    year_now = dt.datetime.now().year
    if year > year_now:
        message = ADV_MESSAGE['wrong_year']
    return {'data': data, 'error': message}


def check_keyword(obj, data: str):
    message = None
    keyword = obj._step_keywords.get(obj.step)
    if keyword:
        if data != keyword['keyword']:
            source = keyword['source']
            message = KEYWORDS_MESS[source]
    return {'data': data, 'error': message}
