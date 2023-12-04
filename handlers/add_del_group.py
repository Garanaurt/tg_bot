from aiogram import Router, Bot, types
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup
from database.db import DbSpamer
from keyboards.admin_kb import kb_go_to_accounts, kb_go_to_main, kb_cancel_but
from .hd_admin import delete_chat_mess, save_message
import asyncio



login_code = ''

router = Router()

class DelGroupStates(StatesGroup):
    WaitId = State()

class AddGroupStates(StatesGroup):
    NAME = State()


@router.callback_query(lambda c: c.data == "add_group")
async def add_accounts(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    chat = call.message.chat.id
    await delete_chat_mess(bot, chat)
    await state.set_state(AddGroupStates.NAME)
    me = await call.message.answer(f'Время между сообщениями и между запусками менять в настройках групп(по умолчанию 10 и 200)\n\nВведи название новой группы:',
                               reply_markup=kb_go_to_accounts())
    await save_message(me)


@router.message(AddGroupStates.NAME)
async def name_processing_group(message: types.Message):
    name = message.text
    try:
        with DbSpamer() as db:
            result = db.db_add_group(name)
    except Exception:
        await asyncio.sleep(0.5)
        with DbSpamer() as db:
            result = db.db_add_group(name)
    if result:
        me = await message.answer(f'Добавлено',
                               reply_markup=kb_go_to_main())
        await save_message(me)



@router.callback_query(lambda c: c.data == "del_group")
async def delete_group(call: types.CallbackQuery, state: FSMContext):
    try:
        with DbSpamer() as db:
            groups = db.db_get_groups_info()
    except Exception:
        await asyncio.sleep(0.5)
        with DbSpamer() as db:
            groups = db.db_get_groups_info()
    await state.set_state(DelGroupStates.WaitId)
    tex = '<b>Группы, чтобы удалить группу пришли ее айди, можно удалить только пустую группу</b>\n'
    for group in groups:
        tex += f'<b>Id:</b>{group[0]}, Название {group[1]}\n'
    me = await call.message.answer(text=tex, reply_markup=kb_cancel_but(), parse_mode='HTML')
    await save_message(me)


@router.message(DelGroupStates.WaitId)
async def processing_delete_group(message: types.Message, state: FSMContext):
    text = message.text
    try:
        int(text)
    except Exception:
        me = await message.answer('Введите число', reply_markup=kb_cancel_but())
        await save_message(me)
        return
    await state.clear()
    try:
        with DbSpamer() as db:
            user_in_group = db.db_check_user_with_group(text)
    except Exception:
        await asyncio.sleep(0.5)
        with DbSpamer() as db:
            user_in_group = db.db_check_user_with_group(text)
    if user_in_group:
        me = await message.answer('В этой группе есть аккаунты, удаление невозможно', reply_markup=kb_cancel_but())
        await save_message(me)
        return
    try:
        result = db.db_del_group_with_id(text)
    except Exception:
        await asyncio.sleep(0.5)
        result = db.db_del_group_with_id(text)
    if result:
        me = await message.answer(f'Группа с айди {text} удалена', reply_markup=kb_go_to_main())
        await save_message(me)



