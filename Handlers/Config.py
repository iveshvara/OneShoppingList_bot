from aiogram.dispatcher.filters.state import State, StatesGroup


class StatesGroupList(StatesGroup):
    item = State()


class StatesGroupStore(StatesGroup):
    store = State()


main_message = None
message_to_delete = None

