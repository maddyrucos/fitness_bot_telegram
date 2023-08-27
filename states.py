from aiogram.dispatcher.filters.state import State, StatesGroup

class Training(StatesGroup):

    default = State()
    height = State()
    weight = State()
    active_training = State()


class Profile(StatesGroup):

    default = State()
    get_value = State()

class Admin(StatesGroup):

    default = State()
    sending_message = State()