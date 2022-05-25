import sqlite3 as sq
from aiogram.utils.markdown import escape_md
from datetime import datetime

connect = sq.connect('OneShoppingList_bot.db')
cursor = connect.cursor()


# START

async def sql_start():
    connect.execute(
        'CREATE TABLE IF NOT EXISTS users(\
            id_user INTEGER UNIQUE, \
            id_list INTEGER, \
            user INTEGER, uuid TEXT, \
            id_store INTEGER, \
            PRIMARY KEY("id_user" AUTOINCREMENT))')
    connect.execute(
        'CREATE TABLE IF NOT EXISTS stores(\
            id_store INTEGER UNIQUE, \
            id_list INTEGER, \
            store TEXT, \
            PRIMARY KEY("id_store" AUTOINCREMENT))')
    connect.execute(
        'CREATE TABLE IF NOT EXISTS items(\
            id_item INTEGER UNIQUE, \
            id_store INTEGER, \
            item TEXT, status \
            INTEGER, timestamp \
            INTEGER, \
            PRIMARY KEY("id_item" AUTOINCREMENT))')
    connect.commit()


async def sql_command_start(user):
    cursor.execute("SELECT id_user, id_list, id_store, user FROM users WHERE user = ?", (user,))
    records = cursor.fetchone()

    if records is None:
        result = connect.execute("SELECT id_list FROM users ORDER BY id_list DESC LIMIT 1")
        records = result.fetchone()
        if records is None:
            id_list = 0
        else:
            id_list = records[0] + 1

        cursor.execute('INSERT INTO users (id_list, user) VALUES (?, ?)', (id_list, user))
        connect.commit()


# SELECT

async def sql_get_stores(user):
    cursor.execute('SELECT stores.id_store, stores.store, ifnull(_items.id_item, 0) as count FROM stores \
                                LEFT OUTER JOIN users ON users.id_list = stores.id_list \
                                LEFT OUTER JOIN (\
                                    SELECT items.id_store, count(items.id_item) as id_item FROM items \
                                        WHERE items.status = 1 GROUP BY items.id_store) \
                                    as _items ON _items.id_store = stores.id_store\
                            WHERE users.user = ? ORDER BY stores.store', (user,))
    records = cursor.fetchall()
    return records


async def sql_get_id_store(user):
    cursor.execute("SELECT id_store FROM users WHERE user = ?", (user,))
    records = cursor.fetchall()
    return records[0][0]


async def sql_get_store_name(id_store):
    cursor.execute("SELECT store FROM stores WHERE id_store = ?", (id_store,))
    records = cursor.fetchall()
    return records[0][0]


async def sql_get_items(id_store):
    cursor.execute("SELECT id_item, item, status FROM items WHERE id_store = ? ORDER BY status DESC, item", (id_store,))
    records = cursor.fetchall()
    return records


async def sql_get_last_id_item(user, status):
    id_store = await sql_get_id_store(user)
    cursor.execute("SELECT items.id_item FROM items WHERE status = ? AND id_store = ? AND id_store IN(\
                        SELECT stores.id_store FROM stores WHERE id_list IN (\
                               SELECT users.id_list FROM users WHERE users.user = ?))\
                    ORDER BY items.timestamp DESC LIMIT 1",
                   (status, id_store, user))
    records = cursor.fetchone()
    if records is None:
        answer = None
    else:
        answer = records[0]
    return answer


# UPDATE

async def sql_update_uuid(uuid, id_user):
    cursor.execute('UPDATE users SET uuid = ? where id_user = ?', (uuid, id_user))
    connect.commit()


async def sql_save_id_list_by_uuid(uuid, id_user):
    cursor.execute("SELECT id_list FROM users WHERE uuid = ?", (uuid,))
    records = cursor.fetchone()
    if records is not None and records[0] is not None:
        cursor.execute('UPDATE users SET id_list = ?, uuid = ? where id_user = ?', (records[0], uuid, id_user))
        connect.commit()


async def sql_save_id_store(id_store, user):
    cursor.execute('UPDATE users SET id_store = ? WHERE user = ?', (id_store, user))
    connect.commit()


async def sql_update_item(id_item, status):
    dt = datetime.today()
    timestamp = dt.timestamp()
    cursor.execute('UPDATE items SET status = ?, timestamp = ? where id_item = ?', (status, timestamp, id_item))
    connect.commit()


async def sql_update_all_item_in_store(user, only_purchased = False):
    # cursor.execute("SELECT items.id_item FROM items WHERE items.status = 2 AND id_store IN(\
    #                    	SELECT stores.id_store FROM stores WHERE id_list IN (\
    #                        SELECT users.id_list FROM users WHERE users.user = ?))", (user,))
    cursor.execute("SELECT items.id_item, items.status FROM items WHERE id_store IN(\
                           	SELECT stores.id_store FROM stores WHERE id_list IN (\
                               SELECT users.id_list FROM users WHERE users.user = ?))", (user,))
    records = cursor.fetchall()
    for i in records:
        if only_purchased and i[1] != 2:
            continue
        await sql_update_item(i[0], 0)


# INSERT

async def sql_add_store(user, stores):
    cursor.execute("SELECT id_list FROM users WHERE user = ?", (user,))
    records = cursor.fetchall()
    id_list = records[0][0]
    massive = stores.splitlines()
    for i in massive:
        cursor.execute('INSERT INTO stores (id_list, store) VALUES (?, ?)', (id_list, escape_md(i)))
    connect.commit()
    id_store = cursor.lastrowid - len(massive) + 1
    await sql_save_id_store(id_store, user)


async def sql_add_list(user, items):
    id_store = await sql_get_id_store(user)
    massive = items.splitlines()
    for i in massive:
        cursor.execute('INSERT INTO items (id_store, item, status) VALUES (?, ?, ?)', (id_store, escape_md(i), 1))
    connect.commit()


# DELETE

async def sql_delete_store(id_store):
    cursor.execute('DELETE FROM items WHERE id_store=?', (id_store,))
    cursor.execute('DELETE FROM stores WHERE id_store=?', (id_store,))
    connect.commit()


async def sql_delete_item(id_store):
    cursor.execute('DELETE FROM items WHERE id_store=? AND status = -1', (id_store,))
    connect.commit()
