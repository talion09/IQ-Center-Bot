from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardRemove

from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher import FSMContext

from tgbot.keyboards.inline.catalog import teachers_clb


# Преподаватели
async def get_teachers_subj(message: types.Message):
    db = message.bot.get("db")
    all_subjects = await db.select_all_teacher_groups()
    markup = InlineKeyboardMarkup(row_width=1)
    unique_subjects = set()
    for id, type_id, type, subject_id, subject, description, day_id, day, time_id, time, teacher_id in all_subjects:
        if subject not in unique_subjects:
            unique_subjects.add(subject)
            markup.insert(InlineKeyboardButton(text=subject, callback_data=teachers_clb.new(action="subject_id", subject_id=subject_id, teacher_id=0)))
    await message.answer("Выберите предмет:", reply_markup=markup)


# back1
async def back_to_teachers_subj(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    all_subjects = await db.select_all_teacher_groups()
    markup = InlineKeyboardMarkup(row_width=1)
    unique_subjects = set()
    for id, type_id, type, subject_id, subject, description, day_id, day, time_id, time, teacher_id in all_subjects:
        if subject not in unique_subjects:
            unique_subjects.add(subject)
            markup.insert(InlineKeyboardButton(text=subject, callback_data=teachers_clb.new(action="subject_id", subject_id=subject_id, teacher_id=0)))
    await call.bot.edit_message_text("Выберите предмет:", call.from_user.id, call.message.message_id, reply_markup=markup)


# subject_id / back2
async def get_teachers(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    subject_id = int(callback_data.get("subject_id"))

    markup = InlineKeyboardMarkup(row_width=1)
    all_subjects = await db.select_in_subjects2(subject_id=subject_id)

    unique_teacher_ids = set()
    for id, type_id, type, subject_id, subject, description, day_id, day, time_id, time, teacher_id in all_subjects:
        if teacher_id not in unique_teacher_ids:
            unique_teacher_ids.add(teacher_id)

    for teacher_idd in unique_teacher_ids:
        teacher = await db.select_teacher(id=teacher_idd)
        user_id = int(teacher.get("telegram_id"))
        teacher_user = await db.select_user(telegram_id=user_id)
        full_name = teacher_user.get("full_name")
        markup.insert(InlineKeyboardButton(text=full_name, callback_data=teachers_clb.new(action="teacher_id", subject_id=subject_id, teacher_id=teacher_idd)))

    markup.insert(InlineKeyboardButton(text="⬅️ Назад", callback_data=teachers_clb.new(action="back1", subject_id=subject_id, teacher_id=0)))
    await call.bot.edit_message_text("Выберите учителя:", call.from_user.id, call.message.message_id, reply_markup=markup)


# teacher_id
async def get_exact_teacher(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    subject_id = int(callback_data.get("subject_id"))
    teacher_id = int(callback_data.get("teacher_id"))

    teacher = await db.select_teacher(id=teacher_id)
    user_id = int(teacher.get("telegram_id"))
    teacher_description = teacher.get("description")

    teacher_user = await db.select_user(telegram_id=user_id)
    full_name = teacher_user.get("full_name")

    text = f"<b>{full_name}</b>\n\n{teacher_description}"
    markup = InlineKeyboardMarkup(row_width=1)
    markup.insert(InlineKeyboardButton(text="⬅️ Назад", callback_data=teachers_clb.new(action="back2", subject_id=subject_id, teacher_id=teacher_id)))
    await call.bot.edit_message_text(text, call.from_user.id, call.message.message_id, reply_markup=markup)


def register_teachers(dp: Dispatcher):
    dp.register_message_handler(get_teachers_subj, text="🎓 Преподаватели")
    dp.register_callback_query_handler(back_to_teachers_subj, teachers_clb.filter(action="back1"))

    dp.register_callback_query_handler(get_teachers, teachers_clb.filter(action="subject_id"))
    dp.register_callback_query_handler(get_teachers, teachers_clb.filter(action="back2"))

    dp.register_callback_query_handler(get_exact_teacher, teachers_clb.filter(action="teacher_id"))





