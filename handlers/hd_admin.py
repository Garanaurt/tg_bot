from aiogram import Router, Bot, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from database.db import db
from keyboards.admin_kb import kb_go_to_main, kb_start_menu, kb_add_accounts

login_code = ''

router = Router()



async def delete_chat_mess(bot: Bot, chat):
    messages = db.db_get_messages_in_chat_admin(chat)
    for msg in messages:
        chat_mess = int(msg[1])
        try:
            await bot.delete_message(chat_id=msg[0], message_id=chat_mess)
        except Exception:
            continue
    db.db_delete_message_in_chat_admin(chat)


async def save_message(message):
    chat_id = message.chat.id
    message_id = message.message_id
    db.db_add_message_in_messages_admin(chat_id, message_id)
    

@router.callback_query(lambda c: c.data == "cancel_adding")
async def cancel_adding(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    await state.clear()
    await cmd_star(call, bot)

@router.callback_query(lambda c: c.data == "go_to_main")
async def go_to_main(call: types.CallbackQuery, bot: Bot):
    await cmd_star(call, bot)

#Старт
@router.message(Command('start'))
async def cmd_start(message: types.Message, bot: Bot):
    chat_id = message.chat.id
    if chat_id > 0:
        await cmd_star(message, bot)


@router.callback_query(F.data == "star")
async def cmd_star(call: types.CallbackQuery, bot: Bot):
    username = call.from_user.username
    chat_id = call.from_user.id
    await delete_chat_mess(bot, chat_id)
    off_users = db.db_get_all_users_off()
    text = f'Привет, {username}\n'
    if off_users:
        text += 'Не запущены аккаунты c айди '
        for user in off_users:
            text += f'{user[0]},'
        text += f'\nВсего {len(off_users)} шт. '
    me = await bot.send_message(chat_id, text, reply_markup=kb_start_menu())
    await save_message(me)
    

@router.callback_query(lambda c: c.data == "add_accs")
async def add_accounts(call: types.CallbackQuery, bot: Bot):
    """Тут можно добавить новую группу, добавить в группу пользователя"""
    chat = call.message.chat.id
    await delete_chat_mess(bot, chat)
    text_table = "Имя группы | Между смс | Между запусками\n"
    groups = db.db_get_groups_info()
    for group in groups:
        text_table += f"{group[1]} | {group[2]} | {group[3]}\n"
    me = await call.message.answer(f'Тут можно добавить новую группу, добавить в группу пользователя\n\nСейчас есть\n{text_table}',
                               reply_markup=kb_add_accounts())
    await save_message(me)



@router.callback_query(lambda c: c.data == "accs_stat")
async def accounts_statistic(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    text = 'Имя аккаунта | Всего групп | Добавлено групп за 24 часа | Отправлено смс от запуска\n'
    users = db.db_get_all_users()
    for user in users:
        try:
            new_groups = user[6].split(':')
        except Exception:
            new_groups = []
        try:
            old_groups = user[9].split(':')
        except Exception:
            old_groups = []
        text += f'{user[8]} | {len(new_groups)} | {len(new_groups) - len(old_groups)} | {user[11]}'

    me = await call.message.answer(text, reply_markup=kb_go_to_main())
    await save_message(me)


        

    








    






    






