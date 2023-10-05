
# import bot as B

# # from bot import bot as B, my_chat_id, my_thread_id
from config import MESS_TEMPLATES

def adv_sender(adv_blank: dict, template: str = MESS_TEMPLATES['adv_line']):
    text = ''
    for key, value in adv_blank.items():
        value = '-' if not value else str(value)
        text += template.format(key, value)
    status = True
    # B.bot.send_message(B.my_chat_id, text,  message_thread_id = B.my_thread_id)
    return {'status': status, 'text': text}
