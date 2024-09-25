def has_redaction_permission(title_message, user_id):
    return title_message.user.tg_id == user_id or (
        title_message.user.is_admin or title_message.user.is_moderator)