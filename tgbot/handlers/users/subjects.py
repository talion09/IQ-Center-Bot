from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardRemove

from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher import FSMContext

from tgbot.keyboards.inline.catalog import subjects_clb


# 📖 Предметы
async def get_types(message: types.Message):
    db = message.bot.get("db")
    all_subjects = await db.select_all_teacher_groups()
    markup = InlineKeyboardMarkup(row_width=1)
    unique_types = set()
    for id, type_id, type, subject_id, subject, description, day_id, day, time_id, time, teacher_id in all_subjects:
        if type not in unique_types:
            unique_types.add(type)
            markup.insert(InlineKeyboardButton(text=type, callback_data=subjects_clb.new(action="type_id", type_id=type_id, subject_id=0, day_id=0, time_id=0)))
    await message.answer("Выберите тип курса:", reply_markup=markup)


# back1
async def back_to_types(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    all_subjects = await db.select_all_teacher_groups()
    markup = InlineKeyboardMarkup(row_width=1)
    unique_types = set()
    for id, type_id, type, subject_id, subject, description, day_id, day, time_id, time, teacher_id in all_subjects:
        if type not in unique_types:
            unique_types.add(type)
            markup.insert(InlineKeyboardButton(text=type, callback_data=subjects_clb.new(action="type_id", type_id=type_id, subject_id=0, day_id=0, time_id=0)))
    await call.bot.edit_message_text("Выберите тип курса:", call.from_user.id, call.message.message_id, reply_markup=markup)


# type_id / back2
async def get_subjects(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    type_id = int(callback_data.get("type_id"))

    all_subjects = await db.select_in_types(type_id=type_id)
    unique_subjects = set()
    markup = InlineKeyboardMarkup(row_width=1)
    for id, type_id, type, subject_id, subject, description, day_id, day, time_id, time, teacher_id in all_subjects:
        if subject not in unique_subjects:
            unique_subjects.add(subject)
            markup.insert(InlineKeyboardButton(text=subject, callback_data=subjects_clb.new(action="subject_id", type_id=type_id, subject_id=subject_id, day_id=0, time_id=0)))
    markup.insert(InlineKeyboardButton(text="⬅️ Назад", callback_data=subjects_clb.new(action="back1", type_id=type_id, subject_id=0, day_id=0, time_id=0)))
    await call.bot.edit_message_text("Выберите предмет:", call.from_user.id, call.message.message_id, reply_markup=markup)


# subject_id
async def get_days(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    type_id = int(callback_data.get("type_id"))
    subject_id = int(callback_data.get("subject_id"))

    markup = InlineKeyboardMarkup(row_width=1)
    all_subjects = await db.select_in_subjects(type_id=type_id, subject_id=subject_id)
    lst_descrip = []
    unique_day_ids = []
    for id, type_id, type, subject_id, subject, description, day_id, day, time_id, time, teacher_id in all_subjects:
        if description not in lst_descrip:
            lst_descrip.append(description)
        if day_id not in unique_day_ids:
            unique_day_ids.append(day_id)

    text = f"{lst_descrip[0]}\n\n<b>---Время проведения---</b>"
    unique_times = {}
    for date_id in unique_day_ids:
        all_subjects = await db.select_in_days(type_id=type_id, subject_id=subject_id, day_id=date_id)
        text += f"\n\n{all_subjects[0].get('day')}:\n"
        count = len(all_subjects)
        for id, type_id, type, subject_id, subject, description, day_id, day, time_id, time, teacher_id in all_subjects:
            if time not in unique_times:
                unique_times[time] = (type_id, subject_id, day_id, time_id)
        sorted_unique_times = sorted(unique_times.keys())
        for time in sorted_unique_times:
            text += f"{time}; "
            if count > 1:
                count -= 1
            else:
                sorted_unique_times.clear()

    markup.insert(InlineKeyboardButton(text="⬅️ Назад", callback_data=subjects_clb.new(action="back2", type_id=type_id, subject_id=subject_id, day_id=0, time_id=0)))
    await call.bot.edit_message_text(text, call.from_user.id, call.message.message_id, reply_markup=markup)


def register_subjects(dp: Dispatcher):
    dp.register_message_handler(get_types, text="📖 Предметы")
    dp.register_callback_query_handler(back_to_types, subjects_clb.filter(action="back1"))

    dp.register_callback_query_handler(get_subjects, subjects_clb.filter(action="type_id"))
    dp.register_callback_query_handler(get_subjects, subjects_clb.filter(action="back2"))

    dp.register_callback_query_handler(get_days, subjects_clb.filter(action="subject_id"))



