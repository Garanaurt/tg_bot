from aiogram import Router, Bot, types
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup
from database.db import db
from keyboards.admin_kb import kb_cancel_but, kb_set_group, kb_go_to_accounts, kb_go_to_main
from .hd_admin import save_message, delete_chat_mess
import re
from telethon.sync import TelegramClient
import asyncio
from userbot import userbot_main

login_code = ''

router = Router()


class DelUserStates(StatesGroup):
    WaitId = State()


class AddUserStates(StatesGroup):
    Group = State()
    LoginPassword = State()
    Proxy = State()
    Phone = State()
    GetCode = State()




@router.callback_query(lambda c: c.data == "add_user")
async def add_user(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    chat = call.message.chat.id
    await delete_chat_mess(bot, chat)
    groups = db.db_get_groups_info()
    me = await call.message.answer(f'Выбери к какой группе добавить этот аккаунт:',
                               reply_markup=kb_set_group(groups))
    await save_message(me)
    

@router.callback_query(lambda c: re.match(r'^user_group_\d+$', c.data))
async def process_add_user(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    group_id = call.data.split('_')[2]
    await state.set_state(AddUserStates.Group)
    await state.update_data(group_id=group_id)
    await state.set_state(AddUserStates.LoginPassword)
    me = await call.message.answer(f'Введи айди и хеш от акккаунта через :\nПример - 12321321:dsfsadsadwqdd',
                               reply_markup=kb_cancel_but())
    await save_message(me)


@router.message(AddUserStates.LoginPassword)
async def process_add_user_log_pass(message: types.Message, bot: Bot, state: FSMContext):
    logpass = message.text.split(':')
    await state.update_data(login=logpass[0])
    await state.update_data(password=logpass[1])
    await state.set_state(AddUserStates.Proxy)
    me = await message.answer(f'Пришли прокси :\nПример - IP:login:password:port',
                               reply_markup=kb_cancel_but())
    await save_message(me)


@router.message(AddUserStates.Proxy)
async def process_add_user_proxy(message: types.Message, bot: Bot, state: FSMContext):
    proxy = message.text
    await state.update_data(proxy=proxy)
    await state.set_state(AddUserStates.Phone)
    me = await message.answer(f'Введи телефон в формате без + (38066123456)',
                               reply_markup=kb_cancel_but())
    await save_message(me)


@router.message(AddUserStates.Phone)
async def process_add_user_proxy(message: types.Message, bot: Bot, state: FSMContext):
    chat_id = message.from_user.id
    phone = message.text
    await state.update_data(phone=phone)
    user_data = await state.get_data()
    phon = user_data['phone']
    client = TelegramClient(user_data['phone'], user_data['login'], user_data['password'])
    await client.connect()
    await client.send_code_request(phon)
    await state.set_state(AddUserStates.GetCode)
    me = await bot.send_message(chat_id, 'Введи полученный код')
    await save_message(me)

async def code_callback():
    global login_code
    return login_code


@router.message(AddUserStates.GetCode)
async def login_to_acc(message: types.Message, state: FSMContext):
    global login_code
    login_code = message.text
    user_data = await state.get_data()
    phon = user_data['phone']
    client = TelegramClient(user_data['phone'], user_data['login'], user_data['password'])
    await client.start(phone=f'+{phon}', code_callback=code_callback)
    try:
        me = await client.get_me()
        username = f'{me.id}:{me.username}:{me.first_name}:{me.last_name}'
        user_data['username'] = username
        print('login ok', me)
    except Exception as e:
        user_data['username'] = None
        print(e)
    db.db_add_user(user_data)
    user = db.db_get_user_info_where_phone(user_data['phone'])
    await client.disconnect()
    login_code = ''
    await state.clear()
    #asyncio.create_task(userbot_main(user[0]))
    me = await message.answer(f'Юзер добавлен', reply_markup=kb_go_to_accounts())
    await save_message(me)
    




@router.callback_query(lambda c: c.data == "del_user")
async def delete_user(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    users = db.db_get_all_users()
    if not users:
        pass
    groups = {}
    for user in users:
        group_id = user[1]
        if group_id not in groups:
            groups[group_id] = [user]
        else:
            groups[group_id].append(user)
    await state.set_state(DelUserStates.WaitId)
    h1_text = 'Юзеры по группам и их айди, чтобы удалить юзера из базы напиши его айди:\n'
    for group, users in groups.items():
        h2_text = h1_text + f'<b>Группа {group}</b>\n'
        msg_cnt = 0
        for user in users:
            h2_text += f'<b>Id:</b>{user[0]}, Тел:{user[5]}, Имя:{user[8]}\n'
            msg_cnt += 1
            if msg_cnt >= 15:
                me = await call.message.answer(text=h2_text, parse_mode='HTML')
                await save_message(me)
                h2_text = ''
                msg_cnt = 0
        if h2_text:
                me = await call.message.answer(text=h2_text, reply_markup=kb_cancel_but(), parse_mode='HTML')
                await save_message(me)
        else:
            me = await call.message.answer(text='<b>end</>', reply_markup=kb_cancel_but(), parse_mode='HTML')
            await save_message(me)
    

@router.message(DelUserStates.WaitId)
async def processing_del_user(message: types.Message, state: FSMContext):
    text = message.text
    try:
        int(text)
    except Exception:
        me = await message.answer('Введите число', reply_markup=kb_cancel_but())
        await save_message(me)
        return
    await state.clear()
    result = db.db_del_user_with_id(text)
    if result:
        me = await message.answer(f'Юзер с айди {text} удален', reply_markup=kb_go_to_main())
        await save_message(me)
