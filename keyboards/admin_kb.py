from aiogram import types
from database.db import db
import sys



sys.path.append("/home/garanaurt/work/spamer_tg_big_bot/")


def kb_go_to_accounts():
    keys = [
        [types.InlineKeyboardButton(text='Отмена', callback_data='star')],
    ]  
    kb = types.InlineKeyboardMarkup(inline_keyboard=keys)
    return kb



def kb_start_menu():
    keys = [
        [types.InlineKeyboardButton(text='Добавить/удалить группы или аккаунты', callback_data='add_accs')],
        [types.InlineKeyboardButton(text='Настройки групп', callback_data="group_settings")],
        [types.InlineKeyboardButton(text='Настройки юзеров', callback_data="users_settings")],
        [types.InlineKeyboardButton(text='Статистика', callback_data="accs_stat")],
    ]  
    kb = types.InlineKeyboardMarkup(inline_keyboard=keys)
    return kb


def kb_add_accounts():
    keys = [
        [types.InlineKeyboardButton(text='Добавить группу', callback_data='add_group'),
        types.InlineKeyboardButton(text='Удалить группу', callback_data="del_group")],

        [types.InlineKeyboardButton(text='Добавить юзера', callback_data="add_user"),
        types.InlineKeyboardButton(text='Удалить юзера', callback_data="del_user")],

        [types.InlineKeyboardButton(text='На главную', callback_data="go_to_main")],
    ]  
    kb = types.InlineKeyboardMarkup(inline_keyboard=keys)
    return kb


def kb_set_group(groups):
    keys = []
    for group in groups:
        keys.append([types.InlineKeyboardButton(text=f'{group[1]}', callback_data=f'user_group_{group[0]}')])
    keys.append([types.InlineKeyboardButton(text='Отмена', callback_data="cancel_adding")])
    kb = types.InlineKeyboardMarkup(inline_keyboard=keys)
    return kb


def kb_cancel_but():
    keys = [
        [types.InlineKeyboardButton(text='Отмена', callback_data="cancel_adding")],
    ]
    kb = types.InlineKeyboardMarkup(inline_keyboard=keys)
    return kb

def kb_go_to_main():
    keys = [
        [types.InlineKeyboardButton(text='На главную', callback_data="go_to_main")],
    ]
    kb = types.InlineKeyboardMarkup(inline_keyboard=keys)
    return kb


def kb_change_group(groups):
    keys = []
    for group in groups:
        keys.append([types.InlineKeyboardButton(text=f'{group[0]} - {group[1]}', callback_data=f'change_group_{group[0]}')])
    keys.append([types.InlineKeyboardButton(text='Отмена', callback_data="cancel_adding")])
    kb = types.InlineKeyboardMarkup(inline_keyboard=keys)
    return kb


def kb_change_group_with_id(group_id):
    group_info = db.db_get_group_info(group_id)
    keys = [
        [types.InlineKeyboardButton(text='Изменить название', callback_data=f'change_name_{group_id}')],
        [types.InlineKeyboardButton(text='Изменить время между смс', callback_data=f"change_sms_{group_id}")],
        [types.InlineKeyboardButton(text='Изменить время между стартом', callback_data=f"change_start_{group_id}")],
    ]
    if group_info[4] == 0:
        keys.append([types.InlineKeyboardButton(text='Включить теги пользователей онлайн', callback_data=f"change_onlineon_{group_id}")])
    else:
        keys.append([types.InlineKeyboardButton(text='Выключить теги пользователей онлайн', callback_data=f"change_onlineoff_{group_id}")])
    if group_info[5] == 0:
        keys.append([types.InlineKeyboardButton(text='Включить теги пользователей недавно', callback_data=f"change_recentlyon_{group_id}")])
    else:
        keys.append([types.InlineKeyboardButton(text='Выключить теги пользователей недавно', callback_data=f"change_recentlyoff_{group_id}")])
    keys.append([types.InlineKeyboardButton(text='Отмена', callback_data="cancel_adding")])
    kb = types.InlineKeyboardMarkup(inline_keyboard=keys)
    return kb


def kb_change_user_with_id(user_id):
    keys = [
        [types.InlineKeyboardButton(text='Изменить группу аккаунта', callback_data=f'change_user_group_{user_id}')],
        [types.InlineKeyboardButton(text='Изменить прокси', callback_data=f"change_user_proxy_{user_id}")],
        [types.InlineKeyboardButton(text='Перевойти в акк', callback_data=f"change_user_restart_{user_id}")],
        [types.InlineKeyboardButton(text='Остановить', callback_data=f"change_user_stop_{user_id}")],
        [types.InlineKeyboardButton(text='Запустить', callback_data=f"change_user_start_{user_id}")],
        [types.InlineKeyboardButton(text='Отмена', callback_data="cancel_adding")],
    ]
    kb = types.InlineKeyboardMarkup(inline_keyboard=keys)
    return kb

