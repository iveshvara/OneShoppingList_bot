from aiogram import types
from create_bot import dp
from DataBase import sqlite_db
from Handlers import CommonFunctions
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


@dp.callback_query_handler(text='shopping')
async def shopping(callback: types.CallbackQuery):
    inline_kb = InlineKeyboardMarkup(row_width=1)
    records = await sqlite_db.sql_get_stores(callback.from_user.id)
    if records is not None:
        for row in records:
            if row[2] > 0:
                inline_kb.add(InlineKeyboardButton(text=row[1] + ' [' + str(row[2]) + ']',
                                                   callback_data='store shopping ' + str(row[0])))
    inline_kb.add(InlineKeyboardButton(text='<Show all in one list>', callback_data='show all in one list'))
    inline_kb.add(InlineKeyboardButton(text='<< Menu', callback_data='menu'))
    await callback.message.edit_text('*Stores:*', parse_mode="MarkdownV2", reply_markup=inline_kb)


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('store shopping '))
async def store_shopping(callback: types.CallbackQuery):
    id_store = int(callback.data.replace('store shopping ', ''))
    await sqlite_db.sql_save_id_store(id_store, callback.from_user.id)
    await get_items_of_handing_by_id(callback.message)


async def get_items_of_handing_by_id(message):
    id_store = await sqlite_db.sql_get_id_store(message.chat.id)
    store_name = await sqlite_db.sql_get_store_name(id_store)
    text = '*"' + store_name + '":*\n'

    inline_kb = InlineKeyboardMarkup(row_width=1)
    records = await sqlite_db.sql_get_items(id_store)
    for row in records:
        if row[2] == 1:
            text = text + '— ' + row[1] + '\n'
            inline_kb.add(InlineKeyboardButton(text=row[1].replace('\\', ''),
                                               callback_data='shopping update item ' + str(row[0])))
        elif row[2] == 2:
            text = text + '~' + row[1] + '~' + '\n'

    massive = [InlineKeyboardButton(text='<--', callback_data='shopping back store'),
               InlineKeyboardButton(text='<Undo>', callback_data='shopping undo'),
               InlineKeyboardButton(text='-->', callback_data='shopping next store')]
    inline_kb.row(*massive)
    inline_kb.add(InlineKeyboardButton(text='<< Back', callback_data='shopping'))

    await message.edit_text(text, parse_mode="MarkdownV2", reply_markup=inline_kb)


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('shopping update item '))
async def shopping_update_item(callback: types.CallbackQuery):
    id_item = int(callback.data.replace('shopping update item ', ''))
    await sqlite_db.sql_update_item(id_item, 2)
    await get_items_of_handing_by_id(callback.message)


@dp.callback_query_handler(text='shopping back store')
async def shopping_back_store(callback: types.CallbackQuery):
    id_store = await CommonFunctions.get_list_stories(callback.from_user.id, True, True)
    if id_store is not None:
        await sqlite_db.sql_save_id_store(id_store, callback.from_user.id)
        await get_items_of_handing_by_id(callback.message)
    else:
        await callback.answer('There are no more shops')


@dp.callback_query_handler(text='shopping undo')
async def shopping_undo(callback: types.CallbackQuery):
    id_item = await sqlite_db.sql_get_last_id_item(callback.from_user.id, 2)
    if id_item is None:
        await callback.answer('Nothing to undo')
    else:
        await sqlite_db.sql_update_item(id_item, 1)
        await get_items_of_handing_by_id(callback.message)


@dp.callback_query_handler(text='shopping next store')
async def shopping_next_store(callback: types.CallbackQuery):
    id_store = await CommonFunctions.get_list_stories(callback.from_user.id, False, True)
    if id_store is not None:
        await sqlite_db.sql_save_id_store(id_store, callback.from_user.id)
        await get_items_of_handing_by_id(callback.message)
    else:
        await callback.answer('There are no more shops')


@dp.callback_query_handler(text='show all in one list')
async def shopping_next_store(callback: types.CallbackQuery):
    text = ''
    stories = await sqlite_db.sql_get_stores(callback.from_user.id)
    for store in stories:
        if store[2] > 0:
            text = text + '\n*' + store[1] + ':*\n'
            records = await sqlite_db.sql_get_items(store[0])
            for i in records:
                if i[2] == 1:
                    text = text + '— ' + i[1] + '\n'

    inline_kb = InlineKeyboardMarkup(row_width=1)
    inline_kb.add(InlineKeyboardButton(text='<< Back', callback_data='shopping'))
    await callback.message.edit_text(text, parse_mode="MarkdownV2", reply_markup=inline_kb)