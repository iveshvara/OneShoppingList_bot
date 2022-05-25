import uuid

from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

from DataBase import sqlite_db
from Handlers import MenuMakeList, Config
from create_bot import dp


class StatesShare(StatesGroup):
    Step1 = State()
    Step2 = State()
    Step3 = State()


async def on_startup(_):
    await sqlite_db.sql_start()


@dp.message_handler(commands=['start', 'menu'])
async def command_start(message: types.Message):
    await sqlite_db.sql_command_start(message.chat.id)
    await menu(message)


@dp.callback_query_handler(text='menu')
async def handler_menu(callback: types.CallbackQuery):
    await callback.message.edit_text('Wellcome.', reply_markup=await menu_kb())


@dp.callback_query_handler(text='menu make а list')
async def add_store(callback: types.CallbackQuery):
    await sqlite_db.sql_update_all_item_in_store(callback.from_user.id, True)
    await handler_menu(callback)

async def menu(message: types.Message):
    Config.main_message = await message.answer('Wellcome.', reply_markup=await menu_kb())


async def menu_kb():
    inline_kb = InlineKeyboardMarkup(row_width=1)
    inline_kb.add(InlineKeyboardButton(text='Shopping', callback_data='shopping'))
    inline_kb.add(InlineKeyboardButton(text='Make a list', callback_data='make а list'))
    inline_kb.add(InlineKeyboardButton(text='Share а list', callback_data='share а list'))
    return inline_kb


@dp.callback_query_handler(text='share а list')
async def command_share_list(callback: types.CallbackQuery):
    inline_kb = InlineKeyboardMarkup(row_width=1)
    inline_kb.add(InlineKeyboardButton(text='<< Menu', callback_data='delete share а list and menu'))
    uuid_str = str(uuid.uuid4())
    await sqlite_db.sql_update_uuid(uuid_str, callback.from_user.id)
    Config.main_message = await callback.message.edit_text('You need your partner to forward this message to the bot:',
                                                           reply_markup=inline_kb)
    Config.message_to_delete = await callback.message.answer(
        'Forward this to the https://t.me/OneShoppingList_bot: \n' + uuid_str)


@dp.callback_query_handler(text='delete share а list and menu')
async def command_share_list(callback: types.CallbackQuery):
    await Config.main_message.delete()
    await Config.message_to_delete.delete()
    await menu(callback.message)


@dp.message_handler(lambda x: x.text and x.text.startswith('Forward this to the https://t.me/OneShoppingList_bot: '))
async def command_start(message: types.Message):
    uuid_str = message.text.replace('Forward this to the https://t.me/OneShoppingList_bot: \n', '')
    await sqlite_db.sql_save_id_list_by_uuid(uuid_str, message.chat.id)
    await message.delete()
    await menu(message)


MenuMakeList.register_handlers(dp)


@dp.message_handler()
async def command_start(message):
    await message.delete()


executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
