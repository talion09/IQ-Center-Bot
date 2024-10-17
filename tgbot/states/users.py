from aiogram.dispatcher.filters.state import StatesGroup, State


class User(StatesGroup):
    Lang = State()
    Name = State()
    Phone = State()
    Next = State()


class Custom(StatesGroup):
    Name = State()
    Phone = State()


class Teachers(StatesGroup):
    Description = State()
    Next = State()
    Confirm = State()


class Admins(StatesGroup):
    Add_group = State()
    New_description = State()
    New_group = State()
    Edit_group = State()


class Deep_link(StatesGroup):
    New_description = State()







