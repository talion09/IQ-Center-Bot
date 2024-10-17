from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardRemove

from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher import FSMContext

from tgbot.handlers.users.start import suitable_menu
from tgbot.keyboards.inline.catalog import sign_up_clb, student_confirm
import datetime


# 📝 Записаться
async def get_types(message: types.Message):
    db = message.bot.get("db")
    all_subjects = await db.select_all_teacher_groups()
    markup = InlineKeyboardMarkup(row_width=1)
    unique_types = set()
    for id, type_id, type, subject_id, subject, description, day_id, day, time_id, time, teacher_id in all_subjects:
        if type not in unique_types:
            unique_types.add(type)
            markup.insert(InlineKeyboardButton(text=type, callback_data=sign_up_clb.new(action="type_id", type_id=type_id, subject_id=0, day_id=0, time_id=0, teacher_id=0, lesson=0)))
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
            markup.insert(InlineKeyboardButton(text=type, callback_data=sign_up_clb.new(action="type_id", type_id=type_id, subject_id=0, day_id=0, time_id=0, teacher_id=0, lesson=0)))
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
            markup.insert(InlineKeyboardButton(text=subject, callback_data=sign_up_clb.new(action="subject_id", type_id=type_id, subject_id=subject_id, day_id=0, time_id=0, teacher_id=0, lesson=0)))
    markup.insert(InlineKeyboardButton(text="⬅️ Назад", callback_data=sign_up_clb.new(action="back1", type_id=type_id, subject_id=0, day_id=0, time_id=0, teacher_id=0, lesson=0)))
    await call.bot.edit_message_text("Выберите предмет:", call.from_user.id, call.message.message_id, reply_markup=markup)


# subject_id / back3
async def get_days(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    type_id = int(callback_data.get("type_id"))
    subject_id = int(callback_data.get("subject_id"))

    all_subjects = await db.select_in_subjects(type_id=type_id, subject_id=subject_id)
    unique_days = set()
    markup = InlineKeyboardMarkup(row_width=1)
    lst_descrip = []
    for id, type_id, type, subject_id, subject, description, day_id, day, time_id, time, teacher_id in all_subjects:
        if day not in unique_days:
            unique_days.add(day)
            markup.insert(InlineKeyboardButton(text=day, callback_data=sign_up_clb.new(action="day_id", type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=0, teacher_id=0, lesson=0)))
        if description not in lst_descrip:
            lst_descrip.append(description)
    text = f"{lst_descrip[0]}\n\nВыберите день:"
    markup.insert(InlineKeyboardButton(text="⬅️ Назад", callback_data=sign_up_clb.new(action="back2", type_id=type_id, subject_id=subject_id, day_id=0, time_id=0, teacher_id=0, lesson=0)))
    await call.bot.edit_message_text(text, call.from_user.id, call.message.message_id, reply_markup=markup)


# day_id / back4
async def get_times(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    type_id = int(callback_data.get("type_id"))
    subject_id = int(callback_data.get("subject_id"))
    day_id = int(callback_data.get("day_id"))

    all_subjects = await db.select_in_days(type_id=type_id, subject_id=subject_id, day_id=day_id)
    unique_times = {}
    markup = InlineKeyboardMarkup(row_width=1)

    for id, type_id, type, subject_id, subject, description, day_id, day, time_id, time, teacher_id in all_subjects:
        if time not in unique_times:
            unique_times[time] = (type_id, subject_id, day_id, time_id)

    sorted_unique_times = sorted(unique_times.keys())

    for time in sorted_unique_times:
        type_id, subject_id, day_id, time_id = unique_times[time]
        markup.insert(InlineKeyboardButton(text=time, callback_data=sign_up_clb.new(action="time_id", type_id=type_id,
                                                                                    subject_id=subject_id,
                                                                                    day_id=day_id, time_id=time_id,
                                                                                    teacher_id=0, lesson=0)))
    markup.insert(InlineKeyboardButton(text="⬅️ Назад", callback_data=sign_up_clb.new(action="back3", type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=0, teacher_id=0, lesson=0)))
    await call.bot.edit_message_text("Выберите время:", call.from_user.id, call.message.message_id, reply_markup=markup)


# time_id / back5
async def get_teachers(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    type_id = int(callback_data.get("type_id"))
    subject_id = int(callback_data.get("subject_id"))
    day_id = int(callback_data.get("day_id"))
    time_id = int(callback_data.get("time_id"))

    all_subjects = await db.select_in_times(type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id)
    unique_teachers = set()
    markup = InlineKeyboardMarkup(row_width=1)
    for id, type_id, type, subject_id, subject, description, day_id, day, time_id, time, teacher_id in all_subjects:
        if teacher_id not in unique_teachers:
            unique_teachers.add(teacher_id)
            teacher = await db.select_teacher(id=teacher_id)
            user_id = int(teacher.get("telegram_id"))
            teacher_user = await db.select_user(telegram_id=user_id)
            full_name = teacher_user.get("full_name")
            markup.insert(InlineKeyboardButton(text=full_name, callback_data=sign_up_clb.new(action="teacher_id", type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id, teacher_id=teacher_id, lesson=0)))
    markup.insert(InlineKeyboardButton(text="⬅️ Назад", callback_data=sign_up_clb.new(action="back4", type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=0, teacher_id=0, lesson=0)))
    await call.bot.edit_message_text("Выберите учителя:", call.from_user.id, call.message.message_id, reply_markup=markup)


# teacher_id / back6
async def get_lesson(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    type_id = int(callback_data.get("type_id"))
    subject_id = int(callback_data.get("subject_id"))
    day_id = int(callback_data.get("day_id"))
    time_id = int(callback_data.get("time_id"))
    teacher_id = int(callback_data.get("teacher_id"))

    markup = InlineKeyboardMarkup(row_width=1)
    markup.insert(InlineKeyboardButton(text="Я уже учусь в IQ Center", callback_data=sign_up_clb.new(action="lesson", type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id, teacher_id=teacher_id, lesson=1)))
    markup.insert(InlineKeyboardButton(text="Я новый ученик", callback_data=sign_up_clb.new(action="lesson", type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id, teacher_id=teacher_id, lesson=2)))
    markup.insert(InlineKeyboardButton(text="⬅️ Назад", callback_data=sign_up_clb.new(action="back5", type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id, teacher_id=teacher_id, lesson=0)))
    await call.bot.edit_message_text("Вы уже учитесь у нас?", call.from_user.id, call.message.message_id, reply_markup=markup)


# lesson / back7
async def get_teacher(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    type_id = int(callback_data.get("type_id"))
    subject_id = int(callback_data.get("subject_id"))
    day_id = int(callback_data.get("day_id"))
    time_id = int(callback_data.get("time_id"))
    lesson = int(callback_data.get("lesson"))
    teacher_id = int(callback_data.get("teacher_id"))

    subjects = await db.select_teacher_group(type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id)

    type = subjects.get("type")
    subject = subjects.get("subject")
    day = subjects.get("day")
    time = subjects.get("time")
    description = subjects.get("description")

    teacher = await db.select_teacher(id=teacher_id)
    user_id = int(teacher.get("telegram_id"))
    teacher_description = teacher.get("description")

    teacher_user = await db.select_user(telegram_id=user_id)
    full_name = teacher_user.get("full_name")

    text = f"<b>Тип курса:</b> {type} \n" \
           f"<b>Предмет:</b> {subject} \n{description}\n" \
           f"<b>Когда:</b> {day} в {time} \n" \
           f"<b>Учитель:</b> {full_name}\n{teacher_description}\n\n" \
           f"Оставить заявку на этот курс?"
    markup = InlineKeyboardMarkup(row_width=1)
    markup.insert(InlineKeyboardButton(text="✅ Да, оставить", callback_data=sign_up_clb.new(action="confirm", type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id, teacher_id=teacher_id, lesson=lesson)))
    markup.insert(InlineKeyboardButton(text="❌ Отмена", callback_data=sign_up_clb.new(action="cancel", type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id, teacher_id=teacher_id, lesson=lesson)))
    markup.insert(InlineKeyboardButton(text="⬅️ Назад", callback_data=sign_up_clb.new(action="back6", type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id, teacher_id=teacher_id, lesson=lesson)))
    await call.bot.edit_message_text(text, call.from_user.id, call.message.message_id, reply_markup=markup)


# confirm
async def confirm_sign(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    type_id = int(callback_data.get("type_id"))
    subject_id = int(callback_data.get("subject_id"))
    day_id = int(callback_data.get("day_id"))
    time_id = int(callback_data.get("time_id"))
    teacher_id = int(callback_data.get("teacher_id"))
    lesson = int(callback_data.get("lesson"))

    user = await db.select_user(telegram_id=call.from_user.id)
    full_name = user.get("full_name")
    phone = user.get("phone")

    text = f"<b>Имя и Фамилия:</b> {full_name} \n" \
           f"<b>Телефонный номер:</b> {phone}\n\n" \
           f"Все верно?"
    markup = InlineKeyboardMarkup(row_width=1)
    markup.insert(InlineKeyboardButton(text="✅ Да", callback_data=sign_up_clb.new(action="confirm_send", type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id, teacher_id=teacher_id, lesson=lesson)))
    # markup.insert(InlineKeyboardButton(text="⚙️ Изменить", callback_data=sign_up_clb.new(action="settings", type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id, lesson=lesson)))
    markup.insert(InlineKeyboardButton(text="⬅️ Назад", callback_data=sign_up_clb.new(action="back7", type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id, teacher_id=teacher_id, lesson=lesson)))
    await call.bot.edit_message_text(text, call.from_user.id, call.message.message_id, reply_markup=markup)


# confirm_send
async def confirm_and_send(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    type_id = int(callback_data.get("type_id"))
    subject_id = int(callback_data.get("subject_id"))
    day_id = int(callback_data.get("day_id"))
    time_id = int(callback_data.get("time_id"))
    teacher_id = int(callback_data.get("teacher_id"))
    lesson = int(callback_data.get("lesson"))

    user = await db.select_user(telegram_id=call.from_user.id)
    student_name = user.get("full_name")
    phone = user.get("phone")

    subjects = await db.select_teacher_group(type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id, teacher_id=teacher_id)
    teacher_group_id = int(subjects.get("id"))
    type = subjects.get("type")
    subject = subjects.get("subject")
    day = subjects.get("day")
    time = subjects.get("time")

    teacher = await db.select_teacher(id=teacher_id)
    user_id = int(teacher.get("telegram_id"))

    teacher_user = await db.select_user(telegram_id=user_id)
    teacher_name = teacher_user.get("full_name")

    text1 = f"<b>Тип курса:</b> {type} \n" \
            f"<b>Предмет:</b> {subject} \n" \
            f"<b>Когда:</b> {day} в {time} \n" \
            f"<b>Учитель:</b> {teacher_name}\n\n" \
            f"<b>Имя и Фамилия:</b> {student_name} \n" \
            f"<b>Телефонный номер:</b> {phone} \n"
    if lesson == 1:
        text1 += f"<b>Этот ученик учится в IQ Center?</b>"
        markup = InlineKeyboardMarkup(row_width=1)
        markup.insert(InlineKeyboardButton(text="✅ Да", callback_data=student_confirm.new(action="yes", telegram_id=call.from_user.id, teacher_group_id=teacher_group_id)))
        markup.insert(InlineKeyboardButton(text="❌ Нет", callback_data=student_confirm.new(action="not", telegram_id=call.from_user.id, teacher_group_id=teacher_group_id)))
        await call.bot.send_message(-1002245940752, text1, reply_markup=markup)
    else:
        text1 += f"<b>Записать этого ученика в IQ Center?</b>"
        markup = InlineKeyboardMarkup(row_width=1)
        markup.insert(InlineKeyboardButton(text="✅ Принять", callback_data=student_confirm.new(action="yes_12", telegram_id=call.from_user.id, teacher_group_id=teacher_group_id)))
        markup.insert(InlineKeyboardButton(text="❌ Отклонить", callback_data=student_confirm.new(action="not", telegram_id=call.from_user.id, teacher_group_id=teacher_group_id)))
        await call.bot.send_message(-1002245940752, text1, reply_markup=markup)
    text2 = "Спасибо за заявку 😊. Ожидайте ответа 🙏"

    await call.bot.edit_message_text(text2, call.from_user.id, call.message.message_id)


# cancel
async def cancel(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    menu = await suitable_menu(call)
    user_in_db = await db.select_user(telegram_id=int(call.from_user.id))
    full_name = user_in_db.get("full_name")
    await call.bot.edit_message_text(f"<b>{full_name}</b>, выберите что вас интересует:", call.from_user.id, call.message.message_id, reply_markup=menu)


def register_sign_up(dp: Dispatcher):
    dp.register_message_handler(get_types, text="📝 Записаться")
    dp.register_callback_query_handler(back_to_types, sign_up_clb.filter(action="back1"))

    dp.register_callback_query_handler(get_subjects, sign_up_clb.filter(action="type_id"))
    dp.register_callback_query_handler(get_subjects, sign_up_clb.filter(action="back2"))

    dp.register_callback_query_handler(get_days, sign_up_clb.filter(action="subject_id"))
    dp.register_callback_query_handler(get_days, sign_up_clb.filter(action="back3"))

    dp.register_callback_query_handler(get_times, sign_up_clb.filter(action="day_id"))
    dp.register_callback_query_handler(get_times, sign_up_clb.filter(action="back4"))

    dp.register_callback_query_handler(get_teachers, sign_up_clb.filter(action="time_id"))
    dp.register_callback_query_handler(get_teachers, sign_up_clb.filter(action="back5"))

    dp.register_callback_query_handler(get_lesson, sign_up_clb.filter(action="teacher_id"))
    dp.register_callback_query_handler(get_lesson, sign_up_clb.filter(action="back6"))

    dp.register_callback_query_handler(get_teacher, sign_up_clb.filter(action="lesson"))
    dp.register_callback_query_handler(get_teacher, sign_up_clb.filter(action="back7"))

    dp.register_callback_query_handler(confirm_sign, sign_up_clb.filter(action="confirm"))
    dp.register_callback_query_handler(confirm_and_send, sign_up_clb.filter(action="confirm_send"))

    dp.register_callback_query_handler(cancel, sign_up_clb.filter(action="cancel"))







