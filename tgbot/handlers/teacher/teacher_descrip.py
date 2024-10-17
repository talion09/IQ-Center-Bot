from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton

from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher import FSMContext
import datetime

from tgbot.filters.is_admin import IsTeacher
from tgbot.handlers.users.start import suitable_menu
from tgbot.keyboards.default.main_menu import teacher_office
from tgbot.keyboards.inline.catalog import teacher_clb, date_clb, present_clb

from tgbot.states.users import Custom, Teachers


# 📝 Мои группы
async def get_description(message: types.Message):
    db = message.bot.get("db")
    teacher = await db.select_teacher(telegram_id=message.from_user.id)
    teacher_id = int(teacher.get("id"))
    teacher_description = teacher.get("description")
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(KeyboardButton(text="Да, хочу"))
    markup.add(KeyboardButton(text="Назад"))
    await message.answer(teacher_description)
    await message.answer("Хотите изменить свое описание?", reply_markup=markup)
    await Teachers.Next.set()


# Teachers.Next
async def change_descrip1(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    if message.text == "Да, хочу":
        cancel = ReplyKeyboardMarkup(resize_keyboard=True)
        cancel.add(KeyboardButton(text="Отменить"))
        text = "Отправьте новое описание"
        await message.answer(text, reply_markup=cancel)
        await Teachers.Description.set()
    else:
        await state.reset_state()
        user_in_db = await db.select_user(telegram_id=int(message.from_user.id))
        full_name = user_in_db.get("full_name")
        await message.answer(f"<b>{full_name}</b>, выберите что вас интересует:", reply_markup=teacher_office)


# Teachers.Description / Confirm
# Отменить
async def change_cancel(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    await state.reset_state()
    user_in_db = await db.select_user(telegram_id=int(message.from_user.id))
    full_name = user_in_db.get("full_name")
    await message.answer(f"<b>{full_name}</b>, выберите что вас интересует:", reply_markup=teacher_office)


# Teachers.Description
async def change_descrip2(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    description = message.text
    user_in_db = await db.select_user(telegram_id=int(message.from_user.id))
    full_name = user_in_db.get("full_name")
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(text="Да ✅"))
    markup.add(KeyboardButton(text="Отменить"))
    await message.answer(description)
    await message.answer(f"<b>{full_name}</b>, все верно?", reply_markup=markup)
    await Teachers.Confirm.set()
    await state.update_data(descrip=description)


# Teachers.Confirm
async def change_descrip3(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    data = await state.get_data()
    description = data.get("descrip")
    teacher = await db.select_teacher(telegram_id=message.from_user.id)
    teacher_id = int(teacher.get("id"))
    teacher_telegram_id = teacher.get("telegram_id")
    await db.update_teacher(telegram_id=teacher_telegram_id, description=description)
    user_in_db = await db.select_user(telegram_id=int(message.from_user.id))
    full_name = user_in_db.get("full_name")
    await message.answer(f"<b>{full_name}</b>, Ваше описание успешно изменено ✅", reply_markup=teacher_office)
    await state.reset_state()


def register_teacher_descrip(dp: Dispatcher):
    # dp.register_message_handler(get_description, IsTeacher(), text="✉️ Мое описание")
    dp.register_message_handler(get_description, text="✉️ Мое описание")
    dp.register_message_handler(change_descrip1, state=Teachers.Next)
    dp.register_message_handler(change_cancel, state=[Teachers.Description, Teachers.Confirm], text="Отменить")
    dp.register_message_handler(change_descrip2, state=Teachers.Description)
    dp.register_message_handler(change_descrip3, state=Teachers.Confirm)













