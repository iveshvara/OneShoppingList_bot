from aiogram import types, Dispatcher
from create_bot import dp
from Handlers import Config, CommonFunctions
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from DataBase import sqlite_db


@dp.callback_query_handler(text='make а list')
async def make_list(callback: types.CallbackQuery):
    inline_kb = InlineKeyboardMarkup(row_width=1)
    records = await sqlite_db.sql_get_stores(callback.from_user.id)
    if records is not None:
        for row in records:
            inline_kb.add(InlineKeyboardButton(text=row[1] + ' [' + str(row[2]) + ']', \
                                               callback_data='store make ' + str(row[0])))
    inline_kb.add(InlineKeyboardButton(text='<add store>', callback_data='add store'))
    inline_kb.add(InlineKeyboardButton(text='<delete store>', callback_data='delete stores'))
    inline_kb.add(InlineKeyboardButton(text='<reset list>', callback_data='reset list'))
    inline_kb.add(InlineKeyboardButton(text='<< Menu', callback_data='menu make а list'))
    await callback.message.edit_text('*Stores:*', parse_mode="MarkdownV2", reply_markup=inline_kb)


@dp.callback_query_handler(text='add store')
async def add_store(callback: types.CallbackQuery):
    await Config.StatesGroupStore.store.set()
    inline_kb = InlineKeyboardMarkup(row_width=1)
    inline_kb.add(InlineKeyboardButton(text='<cancel>', callback_data='cancel add store'))
    await callback.message.edit_text('Please enter the name store:', reply_markup=inline_kb)


@dp.callback_query_handler(state=Config.StatesGroupStore)
async def making_add_item(callback: types.CallbackQuery, state: Config.StatesGroupStore):
    await state.finish()
    await make_list(callback)


async def store_is_input(message: types.Message, state: Config.StatesGroupStore):
    await sqlite_db.sql_add_store(message.chat.id, message.text)
    await state.finish()
    await message.delete()
    await get_items_of_handing_by_id(Config.main_message)


@dp.callback_query_handler(text='delete stores')
async def delete_stores(callback: types.CallbackQuery):
    inline_kb = InlineKeyboardMarkup(row_width=1)
    records = await sqlite_db.sql_get_stores(callback.from_user.id)
    if records is not None:
        for row in records:
            inline_kb.add(InlineKeyboardButton(text=row[1], callback_data='confirm delete store ' + str(row[0])))
    inline_kb.add(InlineKeyboardButton(text='<< Back', callback_data='make а list'))
    await callback.message.edit_text('*Stores and all their elements will be deleted:*', parse_mode="MarkdownV2",
                                     reply_markup=inline_kb)


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('confirm delete store '))
async def confirm_delete_store(callback: types.CallbackQuery):
    id_store = callback.data.replace('confirm delete store ', '')
    store_name = await sqlite_db.sql_get_store_name(id_store)
    text = 'Will be deleted: *"' + store_name + '":*\n'
    inline_kb = InlineKeyboardMarkup(row_width=1)
    records = await sqlite_db.sql_get_items(id_store)
    for row in records:
        text = text + '— ' + row[1] + '\n'

    inline_kb.row(InlineKeyboardButton(text='delete this store', callback_data='delete store ' + id_store))
    inline_kb.add(InlineKeyboardButton(text='<< Back', callback_data='make а list'))

    await callback.message.edit_text(text, parse_mode="MarkdownV2", reply_markup=inline_kb)


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('delete store '))
async def delete_store(callback: types.CallbackQuery):
    id_store = callback.data.replace('delete store ', '')
    await sqlite_db.sql_delete_store(id_store)
    inline_kb = InlineKeyboardMarkup(row_width=1)
    records = await sqlite_db.sql_get_stores(callback.from_user.id)
    if records is not None:
        for row in records:
            inline_kb.add(InlineKeyboardButton(text=row[1], callback_data='delete store ' + str(row[0])))
    inline_kb.add(InlineKeyboardButton(text='<< Back', callback_data='make а list'))
    await callback.message.edit_text('*Stores and all their elements will be deleted:*', parse_mode="MarkdownV2",
                                     reply_markup=inline_kb)


@dp.callback_query_handler(text='reset list')
async def reset_list(callback: types.CallbackQuery):
    await sqlite_db.sql_update_all_item_in_store(callback.from_user.id)
    await callback.answer('Done')
    await make_list(callback)


# in store

@dp.callback_query_handler(lambda x: x.data and x.data.startswith('store make '))
async def get_items_of_handing(callback: types.CallbackQuery):
    id_store = int(callback.data.replace('store make ', ''))
    await get_items_of_handing_continuation(callback, id_store)


async def get_items_of_handing_continuation(callback: types.CallbackQuery, id_store):
    await sqlite_db.sql_save_id_store(id_store, callback.from_user.id)
    await get_items_of_handing_by_id(callback.message)


async def get_items_of_handing_by_id(message):
    id_store = await sqlite_db.sql_get_id_store(message.chat.id)
    store_name = await sqlite_db.sql_get_store_name(id_store)
    text = 'The store *"' + store_name + '"* \n'
    inline_kb = InlineKeyboardMarkup(row_width=1)
    records = await sqlite_db.sql_get_items(id_store)
    for row in records:
        if not row[2] == 1:
            inline_kb.add(
                InlineKeyboardButton(text=row[1].replace('\\', ''), callback_data='making update item ' + str(row[0])))
        else:
            text = text + '— ' + row[1] + '\n'

    massive = [InlineKeyboardButton(text='<--', callback_data='making back store'),
               InlineKeyboardButton(text='<Undo>', callback_data='making undo'),
               InlineKeyboardButton(text='-->', callback_data='making next store')]
    inline_kb.row(*massive)
    massive = [InlineKeyboardButton(text='<Add items>', callback_data='making add item'),
               InlineKeyboardButton(text='<Delete items>', callback_data='making delete items')]
    inline_kb.row(*massive)
    inline_kb.add(InlineKeyboardButton(text='<< Back', callback_data='make а list'))

    await message.edit_text(text, parse_mode="MarkdownV2", reply_markup=inline_kb)


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('making update item '))
async def get_items_of_handing(callback: types.CallbackQuery):
    id_item = int(callback.data.replace('making update item ', ''))
    await sqlite_db.sql_update_item(id_item, 1)
    await get_items_of_handing_by_id(callback.message)


@dp.callback_query_handler(text='making back store')
async def get_items_of_handing_back(callback: types.CallbackQuery):
    id_store = await CommonFunctions.get_list_stories(callback.from_user.id, True)
    if id_store is not None:
        await sqlite_db.sql_save_id_store(id_store, callback.from_user.id)
        await get_items_of_handing_by_id(callback.message)
    else:
        await callback.answer('There are no more shops')


@dp.callback_query_handler(text='making undo')
async def undo(callback: types.CallbackQuery):
    id_item = await sqlite_db.sql_get_last_id_item(callback.from_user.id, 1)
    if id_item is None:
        await callback.answer('Nothing to undo')
    else:
        await sqlite_db.sql_update_item(id_item, 0)
        await get_items_of_handing_by_id(callback.message)


@dp.callback_query_handler(text='making next store')
async def get_items_of_handing_next(callback: types.CallbackQuery):
    id_store = await CommonFunctions.get_list_stories(callback.from_user.id, False)
    if id_store is not None:
        await sqlite_db.sql_save_id_store(id_store, callback.from_user.id)
        await get_items_of_handing_by_id(callback.message)
    else:
        await callback.answer('There are no more shops')


@dp.callback_query_handler(text='making add item')
async def making_add_item(callback: types.CallbackQuery):
    await Config.StatesGroupList.item.set()
    inline_kb = InlineKeyboardMarkup(row_width=1)
    inline_kb.add(InlineKeyboardButton(text='<cancel>', callback_data='cancel add item'))
    Config.main_message = callback.message
    await Config.main_message.edit_text('Please enter a list of items:', reply_markup=inline_kb)


@dp.callback_query_handler(state=Config.StatesGroupList)
async def making_add_item(callback: types.CallbackQuery, state: Config.StatesGroupList):
    await state.finish()
    id_store = await sqlite_db.sql_get_id_store(callback.from_user.id)
    await get_items_of_handing_continuation(callback, id_store)


async def item_is_input(message: types.Message, state: Config.StatesGroupList):
    await sqlite_db.sql_add_list(message.chat.id, message.text)
    await state.finish()
    await message.delete()
    await get_items_of_handing_by_id(Config.main_message)


@dp.callback_query_handler(text='making delete items')
async def making_delete_items(callback: types.CallbackQuery):
    id_store = await sqlite_db.sql_get_id_store(callback.from_user.id)
    store_name = await sqlite_db.sql_get_store_name(id_store)
    text = 'The store *"' + store_name + '"*\. This items will be deleted\:\n'
    inline_kb = InlineKeyboardMarkup(row_width=1)
    records = await sqlite_db.sql_get_items(id_store)
    for i in records:
        if not i[2] == -1:
            inline_kb.add(
                InlineKeyboardButton(text=i[1], callback_data='making delete item ' + str(i[0])))
        else:
            text = text + '— ' + i[1] + '\n'
    inline_kb.add(InlineKeyboardButton(text='<Delete selected items>', callback_data='delete selected items'))
    inline_kb.add(InlineKeyboardButton(text='<< Back', callback_data='store make ' + str(id_store)))
    await callback.message.edit_text(text, parse_mode="MarkdownV2", reply_markup=inline_kb)


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('making delete item '))
async def add_store(callback: types.CallbackQuery):
    id_item = callback.data.replace('making delete item ', '')
    await sqlite_db.sql_update_item(id_item, -1)
    await making_delete_items(callback)


@dp.callback_query_handler(text='delete selected items')
async def delete_selected_items(callback: types.CallbackQuery):
    id_store = await sqlite_db.sql_get_id_store(callback.from_user.id)
    await sqlite_db.sql_delete_item(id_store)
    await making_delete_items(callback)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(item_is_input, state=Config.StatesGroupList.item)
    dp.register_message_handler(store_is_input, state=Config.StatesGroupStore.store)
