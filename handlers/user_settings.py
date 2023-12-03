from aiogram import Router, Bot, types
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup
from telethon.sync import TelegramClient
from telethon.errors import PhoneNumberBannedError
from database.db import db
from .hd_admin import save_message
from userbot import userbot_main
from keyboards.admin_kb import kb_go_to_main, kb_change_user_with_id, kb_cancel_but
import re
import asyncio
import os
import time


login_code = ''

router = Router()

class ChangeUserSettings(StatesGroup):
    WaitId = State()
    Group = State()
    Proxy = State()


class RestartStates(StatesGroup):
    GetCode = State()




@router.callback_query(lambda c: c.data == "users_settings")
async def user_settings(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    try:
        users = db.db_get_all_users()
    except Exception:
        await asyncio.sleep(0.5)
        users = db.db_get_all_users()
    if not users:
        me = await call.message.answer(text='Нет юзеров', reply_markup=kb_cancel_but(), parse_mode='HTML')
        await save_message(me)
    groups = {}
    for user in users:
        group_id = user[1]
        if group_id not in groups:
            groups[group_id] = [user]
        else:
            groups[group_id].append(user)
    await state.set_state(ChangeUserSettings.WaitId)
    h1_text = 'Юзеры по группам и их айди, чтобы изменить юзера напиши его айди:\n'
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


@router.message(ChangeUserSettings.WaitId)
async def processing_change_user(message: types.Message, state: FSMContext):
    user_id = message.text
    try:
        user_info = db.db_get_user_info(user_id)
    except Exception:
        await asyncio.sleep(0.5)
        user_info = db.db_get_user_info(user_id)
    started = 'Да' if user_info[10] == 1 else 'Нет'
    mes = f'Id:{user_info[0]}, Тел:{user_info[5]}, Имя:{user_info[8]}\n'
    try:
        int(user_id)
    except Exception:
        me = await message.answer("Введи число", reply_markup=kb_cancel_but())
        await save_message(me)
        return
    me = await message.answer(f"Настройки аккаунта {mes}. Аккаунт запущен - {started}", reply_markup=kb_change_user_with_id(user_id))
    await save_message(me)


@router.callback_query(lambda c: re.match(r'^change_user_group_\d+$', c.data))
async def change_user_group(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    user_id = call.data.split('_')[3]
    try:
        groups = db.db_get_groups_info()
    except Exception:
        await asyncio.sleep(0.5)
        groups = db.db_get_groups_info()
    await state.set_state(ChangeUserSettings.Group)
    await state.update_data(user_id=user_id)
    text = 'Для смены группы пользователя пришлите ее айди \n\nId | Название | Между смс | Между стартом\n'
    for group in groups:
        text += f"{group[0]} | {group[1]} | {group[2]} | {group[3]}\n"
    me = await call.message.answer(text, reply_markup=kb_cancel_but())
    await save_message(me)

@router.message(ChangeUserSettings.Group)
async def processing_change_user_group(message: types.Message, state: FSMContext):
    new_group = message.text
    try:
        int(new_group)
    except Exception:
        me = await message.answer("Введи число", reply_markup=kb_cancel_but())
        await save_message(me)
        return
    try:
        group = db.db_get_group_with_id(new_group)
    except Exception:
        await asyncio.sleep(0.5)
        group = db.db_get_group_with_id(new_group)
    if not group:
        me = await message.answer("Группы с таким айди не существует, пришли другой айди", reply_markup=kb_cancel_but())
        await save_message(me)
        return
    user_data = await state.get_data()
    user_id = user_data['user_id']
    try:
        result = db.db_set_user_group(user_id, new_group)
    except Exception:
        await asyncio.sleep(0.5)
        result = db.db_set_user_group(user_id, new_group)
    await state.clear()
    if result:
        me = await message.answer("Группа изменена", reply_markup=kb_cancel_but())
        await save_message(me)





@router.callback_query(lambda c: re.match(r'^change_user_proxy_\d+$', c.data))
async def change_user_proxy(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    user_id = call.data.split('_')[3]
    await state.set_state(ChangeUserSettings.Proxy)
    await state.update_data(user_id=user_id)
    me = await call.message.answer('Пришли новые данные прокси в формате IP:login:password:port ', reply_markup=kb_cancel_but())
    await save_message(me)


@router.message(ChangeUserSettings.Proxy)
async def processing_change_user_proxy(message: types.Message, state: FSMContext):
    new_group = message.text
    user_data = await state.get_data()
    user_id = user_data['user_id']
    try:
        result = db.db_set_user_proxy(user_id, new_group)
    except Exception:
        await asyncio.sleep(0.5)
        result = db.db_set_user_proxy(user_id, new_group)
    await state.clear()
    if result:
        me = await message.answer("Прокси изменены", reply_markup=kb_cancel_but())
        await save_message(me)



@router.callback_query(lambda c: re.match(r'^change_user_restart_\d+$', c.data))
async def change_user_restart(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    user_id = call.data.split('_')[3]
    try:
        user_info = db.db_get_user_info(user_id)
    except Exception:
        await asyncio.sleep(0.5)
        user_info = db.db_get_user_info(user_id)
    print('change user restart', user_info)
    current_directory = os.path.dirname(os.path.abspath(__file__))
    parent_directory = os.path.join(current_directory, os.pardir)
    print(current_directory)
    session_file_name = f"{user_info[5]}.session"
    session_file_path = os.path.join(parent_directory, session_file_name)
    if os.path.exists(session_file_path):
        os.remove(session_file_path)
        print(f"Файл сессии удален: {session_file_path}")
    else:
        me = await call.message.answer("Файл сессии не найден", reply_markup=kb_cancel_but())
        await save_message(me)
    await processing_restart_user(call, bot, state, user_info)


async def processing_restart_user(call: types.CallbackQuery, bot: Bot, state: FSMContext, user_info):
    await state.set_state(RestartStates.GetCode)
    await state.update_data(user_id=user_info[0])
    chat_id = call.from_user.id
    phon = user_info[5]
    try:
        db.db_update_count(user_info[0], 0)
    except Exception:
        await asyncio.sleep(0.5)
        db.db_update_count(user_info[0], 0)
    client = TelegramClient(user_info[5], user_info[2], user_info[3])
    try:
        await client.connect()
        await client.send_code_request(phon)
    except Exception as e:
        me = await bot.send_message(chat_id, f'Не отправляется код ошибка от тг:{e}', reply_markup=kb_cancel_but())
        await save_message(me)
        return
    me = await bot.send_message(chat_id, 'Введи полученный код')
    await save_message(me)

async def code_callback():
    global login_code
    return login_code


@router.message(RestartStates.GetCode)
async def processing_restart_acc(message: types.Message, state: FSMContext):
    global login_code
    login_code = message.text
    user_data = await state.get_data()
    try:
        user_info = db.db_get_user_info(user_data['user_id'])
    except Exception:
        await asyncio.sleep(0.5)
        user_info = db.db_get_user_info(user_data['user_id'])
    phon = user_info[5]
    client = TelegramClient(user_info[5], user_info[2], user_info[3])
    await client.start(phone=f'+{phon}', code_callback=code_callback)
    await client.disconnect()
    login_code = ''
    await state.clear()
    try:
        db.db_set_user_start(user_data['user_id'])
    except Exception:
        await asyncio.sleep(0.5)
        db.db_set_user_start(user_data['user_id'])
    asyncio.create_task(userbot_main(user_data['user_id']))
    me = await message.answer(f'Перевошли в аккаунт удачно, и запустили его в работу', reply_markup=kb_go_to_main())
    await save_message(me)



@router.callback_query(lambda c: re.match(r'^change_user_stop_\d+$', c.data))
async def change_user_stop(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    user_id = call.data.split('_')[3]
    try:
        db.db_set_user_stop(user_id)
        db.db_update_count(user_id, 0)
    except Exception:
        await asyncio.sleep(0.5)
        db.db_set_user_stop(user_id)
        db.db_update_count(user_id, 0)
    me = await call.message.answer(f'Юзер выключен', reply_markup=kb_go_to_main())
    await save_message(me)



@router.callback_query(lambda c: re.match(r'^change_user_start_\d+$', c.data))
async def change_user_stop(call: types.CallbackQuery):
    user_id = call.data.split('_')[3]
    try:
        db.db_set_user_start(user_id)
    except Exception:
        await asyncio.sleep(0.5)
        db.db_set_user_start(user_id)
    asyncio.create_task(userbot_main(user_id))
    print('1')
    await asyncio.sleep(2)
    try:
        user = db.db_get_user_info(user_id)
    except Exception:
        await asyncio.sleep(0.5)
        user = db.db_get_user_info(user_id)
    if user[10] == 0:
        me = await call.message.answer(f'Юзер не запускается, подожди минуту и попробуй еще, если повторяется перевойди в акк', reply_markup=kb_go_to_main())
        await save_message(me)
    else:
        me = await call.message.answer(f'Юзер запущен', reply_markup=kb_go_to_main())
        await save_message(me)
