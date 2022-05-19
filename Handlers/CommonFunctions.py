from DataBase import sqlite_db


async def get_list_stories(user, previous, zero_is_not_taken=False):
    records = await sqlite_db.sql_get_stores(user)
    records_dict = dict()
    for i in records:
        records_dict[i[0]] = i[1]
    records_dict_keys = list(records_dict.keys())
    id_store = await sqlite_db.sql_get_id_store(user)
    index = records_dict_keys.index(id_store)
    new_index = None

    if previous:
        if zero_is_not_taken:
            cycle = True
            temporary_index = index
            start_index = temporary_index
            while cycle:
                temporary_index -= 1
                if temporary_index < 0:
                    temporary_index = records.__len__() - 1
                if start_index == temporary_index:
                    cycle = False
                if cycle and records[temporary_index][2] > 0:
                    new_index = temporary_index
                    cycle = False
        else:
            if index == 0:
                temporary_index = records.__len__() - 1
            else:
                temporary_index = index - 1
            new_index = temporary_index
    else:
        if zero_is_not_taken:
            cycle = True
            temporary_index = index
            start_index = temporary_index
            while cycle:
                temporary_index += 1
                if temporary_index > records.__len__() - 1:
                    temporary_index = 0
                if start_index == temporary_index:
                    cycle = False
                if cycle and records[temporary_index][2] > 0:
                    new_index = temporary_index
                    cycle = False
        else:
            if index == records.__len__() - 1:
                temporary_index = 0
            else:
                temporary_index = index + 1
            new_index = temporary_index

    if new_index is None:
        id_store = None
    else:
        id_store = records[new_index][0]

    return id_store
