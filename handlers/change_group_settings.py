from aiogram import Router, Bot, types
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup
from database.db import db
from .hd_admin import save_message
from keyboards.admin_kb import kb_go_to_main, kb_change_group, kb_change_group_with_id, kb_cancel_but
import re

login_code = ''

router = Router()


class ChangeGroupSettings(StatesGroup):
    NAME = State()
    SMS = State()
    START = State()



@router.callback_query(lambda c: c.data == "group_settings")
async def group_settings(call: types.CallbackQuery, bot: Bot):
    groups = db.db_get_groups_info()
    text = 'Выбери группу для изменения\n\nId | Название | Между смс | Между стартом\n'
    for group in groups:
        text += f"{group[0]} | {group[1]} | {group[2]} | {group[3]}\n"
    me = await call.message.answer(text, reply_markup=kb_change_group(groups))
    await save_message(me)


@router.callback_query(lambda c: re.match(r'^change_group_\d+$', c.data))
async def process_change_group(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    group_id = call.data.split('_')[2]
    gr_info = db.db_get_group_info(group_id)
    online = 'Да' if gr_info[4] == 1 else 'Нет'
    recently = 'Да' if gr_info[5] == 1 else 'Нет'
    text = f'Информация о группе:\nId - {gr_info[0]} \nНазвание - {gr_info[1]} \nМежду смс - {gr_info[2]} \nМежду стартом - {gr_info[3]}\nТегать кто онлайн - {online}\nТегать кто онлайн недавно - {recently}'
    me = await call.message.answer(text, reply_markup=kb_change_group_with_id(group_id))
    await save_message(me)
    print(gr_info)



@router.callback_query(lambda c: re.match(r'^change_name_\d+$', c.data))
async def change_name_group(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    group_id = call.data.split('_')[2]
    await state.set_state(ChangeGroupSettings.NAME)
    await state.update_data(group_id=group_id)
    me = await call.message.answer("Введи новое имя", reply_markup=kb_cancel_but())
    await save_message(me)

@router.message(ChangeGroupSettings.NAME)
async def processing_change_name_group(message: types.Message, state: FSMContext):
    data = await state.get_data()
    new_name = message.text
    db.db_set_name_for_group_id(data['group_id'], new_name)
    await state.clear()
    me = await message.answer("Имя обновлено", reply_markup=kb_go_to_main())
    await save_message(me)




@router.callback_query(lambda c: re.match(r'^change_sms_\d+$', c.data))
async def change_sms_group(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    group_id = call.data.split('_')[2]
    await state.set_state(ChangeGroupSettings.SMS)
    await state.update_data(group_id=group_id)
    me = await call.message.answer("Введи новое время между смс", reply_markup=kb_cancel_but())
    await save_message(me)

@router.message(ChangeGroupSettings.SMS)
async def processing_change_sms_group(message: types.Message, state: FSMContext):
    data = await state.get_data()
    new_time = message.text
    try:
        int(new_time)
    except Exception:
        me = await message.answer("Введи число", reply_markup=kb_cancel_but())
        await save_message(me)
        return
    db.db_set_sms_for_group_id(data['group_id'], new_time)
    await state.clear()
    me = await message.answer("Время между смс обновлено", reply_markup=kb_go_to_main())
    await save_message(me)





@router.callback_query(lambda c: re.match(r'^change_start_\d+$', c.data))
async def change_start_group(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    group_id = call.data.split('_')[2]
    await state.set_state(ChangeGroupSettings.START)
    await state.update_data(group_id=group_id)
    me = await call.message.answer("Введи новое время между стартом рассылок", reply_markup=kb_cancel_but())
    await save_message(me)

@router.message(ChangeGroupSettings.START)
async def processing_change_start_group(message: types.Message, state: FSMContext):
    data = await state.get_data()
    new_time = message.text
    try:
        int(new_time)
    except Exception:
        me = await message.answer("Введи число", reply_markup=kb_cancel_but())
        await save_message(me)
        return
    db.db_set_start_for_group_id(data['group_id'], new_time)
    await state.clear()
    me = await message.answer("Время между стартом рассылки обновлено", reply_markup=kb_go_to_main())
    await save_message(me)



@router.callback_query(lambda c: re.match(r'^change_onlineon_\d+$', c.data))
async def change_onlineon_group(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    group_id = call.data.split('_')[2]
    db.db_set_onlineon_for_group_id(group_id)
    me = await call.message.answer("Теги для юзеров онлайн вкл", reply_markup=kb_go_to_main())
    await save_message(me)


@router.callback_query(lambda c: re.match(r'^change_onlineoff_\d+$', c.data))
async def change_onlineoff_group(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    group_id = call.data.split('_')[2]
    db.db_set_onlineoff_for_group_id(group_id)
    me = await call.message.answer("Теги для юзеров онлайн выкл", reply_markup=kb_go_to_main())
    await save_message(me)



@router.callback_query(lambda c: re.match(r'^change_recentlyon_\d+$', c.data))
async def change_recentlyon_group(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    group_id = call.data.split('_')[2]
    db.db_set_recentlyon_for_group_id(group_id)
    me = await call.message.answer("Теги для юзеров онлайн недавно вкл", reply_markup=kb_go_to_main())
    await save_message(me)


@router.callback_query(lambda c: re.match(r'^change_recentlyoff_\d+$', c.data))
async def change_recentlyoff_group(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    group_id = call.data.split('_')[2]
    db.db_set_recentlyoff_for_group_id(group_id)
    me = await call.message.answer("Теги для юзеров онлайн недавно выкл", reply_markup=kb_go_to_main())
    await save_message(me)
