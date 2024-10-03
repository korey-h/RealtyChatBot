def has_redaction_permission(title_message, user_id):
    return title_message.user.tg_id == user_id or (
        title_message.user.is_admin or title_message.user.is_moderator)


def is_redact_period_active(user):
    """Проверка, не истек ли период, когда доступно редактирование
    сообщений. Учитывает оганичения Telegram"""
    # user - это объект из модуля models.py
    return True


def is_resend_while_redaction_active(user):
    """Проверка, доступна ли отправка отредактированного объявления
    как нового. Т.е. допускается такая отправка, если истек период редактирования,
    определенный Telegram"""
    # user - это объект из модуля models.py
    return True


def is_resend_active(user):
    """Проверка, доступна ли отправка отредактированного объявления
    как нового (или повторная отправка)."""
    # user - это объект из модуля models.py
    return True


def is_redac_available_again(user):
    """Проверка, прошло ли время временного запрета с момента предыдущего 
    редактирования"""
    # user - это объект из модуля models.py
    return True

