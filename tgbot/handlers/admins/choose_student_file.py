from aiogram import Dispatcher
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import datetime

from tgbot.filters.is_admin import IsAdmin
from tgbot.handlers.admins.functions import get_teacher, get_times, get_days, get_subjects, get_types
from tgbot.keyboards.inline.catalog import get_students_clb, student_custom_clb, choose_student_clb, \
    student_lessons_confirm


# choose_student / back1
async def choose_student_types(call: CallbackQuery, callback_data: dict):
    await get_types(call, callback_data, choose_student_clb, student_custom_clb)


# type_id / back2
async def choose_student_subjects(call: CallbackQuery, callback_data: dict):
    await get_subjects(call, callback_data, choose_student_clb)


# subject_id / back3
async def choose_student_days(call: CallbackQuery, callback_data: dict):
    await get_days(call, callback_data, choose_student_clb)


# day_id / back4
async def choose_student_times(call: CallbackQuery, callback_data: dict):
    await get_times(call, callback_data, choose_student_clb)


# time_id / back5
async def choose_student_teacher(call: CallbackQuery, callback_data: dict):
    await get_teacher(call, callback_data, choose_student_clb)


# teacher_id / choose_back6
async def choose_student_data(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    type_id = int(callback_data.get("type_id"))
    subject_id = int(callback_data.get("subject_id"))
    day_id = int(callback_data.get("day_id"))
    time_id = int(callback_data.get("time_id"))
    teacher_id = int(callback_data.get("teacher_id"))

    subjects = await db.select_teacher_group(type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id, teacher_id=teacher_id)
    teacher_group_id = int(subjects.get("id"))

    text = f"Выберите студента:"
    markup = InlineKeyboardMarkup(row_width=1)
    groups_id = await db.select_id_groups(teacher_group_id=teacher_group_id)
    for id in groups_id:
        group = await db.select_group(id=int(id.get("id")))
        student_id = int(group.get("student_id"))
        student = await db.select_student(id=student_id)
        telegram_id = int(student.get("telegram_id"))
        user = await db.select_user(telegram_id=telegram_id)
        full_name =  user.get("full_name")
        markup.insert(InlineKeyboardButton(text=full_name, callback_data=get_students_clb.new(action="get_student_data", teacher_group_id=teacher_group_id, student_id=student_id)))
    markup.insert(InlineKeyboardButton(text="⬅️ Назад", callback_data=choose_student_clb.new(action="back5", type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id, teacher_id=teacher_id)))
    await call.bot.edit_message_text(text, call.from_user.id, call.message.message_id, reply_markup=markup)


# get_student_data / choose_back7
async def get_student_data(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    teacher_group_id = int(callback_data.get("teacher_group_id"))
    student_id = int(callback_data.get("student_id"))

    teacher_groups = await db.select_groups2(student_id=student_id)
    subjects = f""
    for id_teacher_group in teacher_groups:
        teacher_group = await db.select_teacher_group(id=int(id_teacher_group.get("teacher_group_id")))
        subject = teacher_group.get("subject")
        subjects += f"{subject}\n"

    student = await db.select_student(id=student_id)
    telegram_id = int(student.get("telegram_id"))
    user = await db.select_user(telegram_id=telegram_id)
    full_name = user.get("full_name")
    phone = user.get("phone")
    remaining_lessons = int(student.get("remaining_lessons"))
    calculation = 820000 / 12 * remaining_lessons
    text = f"Студент: {full_name}\n" \
           f"Номер телефона: {phone}\n" \
           f"Предметы: \n{subjects}" \
           f"Баланс: {calculation}\n\n" \
           f"Пропущенные уроки за последние 2 месяца:\n"
    current_date = datetime.date.today()
    two_months_ago = current_date - datetime.timedelta(days=60)
    skips = await db.select_skips_for_student_in_last_two_months(student_id, two_months_ago)
    for id, student_id, lesson_date in skips:
        date_string = lesson_date.strftime('%Y-%m-%d')
        text += f"{date_string} \n"

    text += f"Изменить количество оставшихся уроков?"
    subject = await db.select_teacher_group(id=teacher_group_id)
    type_id = int(subject.get("type_id"))
    subject_id = int(subject.get("subject_id"))
    day_id = int(subject.get("day_id"))
    time_id = int(subject.get("time_id"))
    teacher_id = int(subject.get("teacher_id"))

    markup = InlineKeyboardMarkup(row_width=1)
    markup.insert(InlineKeyboardButton(text="Изменить", callback_data=get_students_clb.new(action="edit_lessons", teacher_group_id=teacher_group_id, student_id=student_id)))
    markup.insert(InlineKeyboardButton(text="⬅️ Назад", callback_data=choose_student_clb.new(action="choose_back6", type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id, teacher_id=teacher_id)))
    await call.bot.edit_message_text(text, call.from_user.id, call.message.message_id, reply_markup=markup)


# edit_lessons / choose_back8
async def edit_lessons(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    student_id = int(callback_data.get("student_id"))
    teacher_group_id = int(callback_data.get("teacher_group_id"))

    markup = InlineKeyboardMarkup(row_width=4)
    for lesson in range(1, 13):
        markup.insert(InlineKeyboardButton(text=str(lesson), callback_data=student_lessons_confirm.new(action="edit_lessons_quantity", student_id=student_id, remaining_lessons=int(lesson), teacher_group_id=teacher_group_id)))

    markup = InlineKeyboardMarkup(row_width=3)
    markup.insert(InlineKeyboardButton(text="< 12",
                                       callback_data=student_lessons_confirm.new(action="< 12_edit_",
                                                                                 student_id=student_id,
                                                                                 remaining_lessons=0,
                                                                                 teacher_group_id=teacher_group_id)))
    markup.insert(InlineKeyboardButton(text="12",
                                       callback_data=student_lessons_confirm.new(action="12_edit_",
                                                                                 student_id=student_id,
                                                                                 remaining_lessons=0,
                                                                                 teacher_group_id=teacher_group_id)))
    markup.insert(InlineKeyboardButton(text="> 12",
                                       callback_data=student_lessons_confirm.new(action="> 12_edit_",
                                                                                 student_id=student_id,
                                                                                 remaining_lessons=0,
                                                                                 teacher_group_id=teacher_group_id)))
    markup.insert(InlineKeyboardButton(text="⬅️ Назад", callback_data=get_students_clb.new(action="choose_back7", teacher_group_id=teacher_group_id, student_id=student_id)))
    await call.bot.edit_message_text(call.message.text, call.from_user.id, call.message.message_id, reply_markup=markup)


# < 12 / 12 / > 12
async def less_or_more(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    student_id = int(callback_data.get("student_id"))
    remaining_lessons = int(callback_data.get("remaining_lessons"))
    teacher_group_id = int(callback_data.get("teacher_group_id"))
    action = callback_data.get("action")

    markup = InlineKeyboardMarkup(row_width=4)
    if action == "< 12_edit_":
        for lesson in range(-12, 0):
            markup.insert(InlineKeyboardButton(text=str(lesson),
                                               callback_data=student_lessons_confirm.new(action="edit_quantity",
                                                                                         student_id=student_id,
                                                                                         remaining_lessons=int(lesson),
                                                                                         teacher_group_id=teacher_group_id)))
    elif action == "12_edit_":
        for lesson in range(1, 13):
            markup.insert(InlineKeyboardButton(text=str(lesson),
                                               callback_data=student_lessons_confirm.new(action="edit_quantity",
                                                                                         student_id=student_id,
                                                                                         remaining_lessons=int(lesson),
                                                                                         teacher_group_id=teacher_group_id)))
    elif action == "> 12_edit_":
        for lesson in range(12, 25):
            markup.insert(InlineKeyboardButton(text=str(lesson),
                                               callback_data=student_lessons_confirm.new(action="edit_quantity",
                                                                                         student_id=student_id,
                                                                                         remaining_lessons=int(lesson),
                                                                                         teacher_group_id=teacher_group_id)))
    else:
        pass
    markup.insert(InlineKeyboardButton(text="⬅️ Назад", callback_data=get_students_clb.new(action="choose_back8", teacher_group_id=teacher_group_id, student_id=student_id)))
    await call.bot.edit_message_text(call.message.text, call.from_user.id, call.message.message_id, reply_markup=markup)


async def edit_lessons_quantity(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    student_id = int(callback_data.get("student_id"))
    remaining_lessons = int(callback_data.get("remaining_lessons"))
    teacher_group_id = int(callback_data.get("teacher_group_id"))

    await db.update_student(id=student_id, remaining_lessons=remaining_lessons)
    await get_student_data(call, callback_data)


def register_choose_student_file(dp: Dispatcher):
    #                                               IS_ADMIN_
    dp.register_callback_query_handler(choose_student_types, student_custom_clb.filter(action="choose_student"))
    dp.register_callback_query_handler(choose_student_types, choose_student_clb.filter(action="back1"))

    dp.register_callback_query_handler(choose_student_subjects, choose_student_clb.filter(action="type_id"))
    dp.register_callback_query_handler(choose_student_subjects, choose_student_clb.filter(action="back2"))

    dp.register_callback_query_handler(choose_student_days, choose_student_clb.filter(action="subject_id"))
    dp.register_callback_query_handler(choose_student_days, choose_student_clb.filter(action="back3"))

    dp.register_callback_query_handler(choose_student_times, choose_student_clb.filter(action="day_id"))
    dp.register_callback_query_handler(choose_student_times, choose_student_clb.filter(action="back4"))

    dp.register_callback_query_handler(choose_student_teacher, choose_student_clb.filter(action="time_id"))
    dp.register_callback_query_handler(choose_student_teacher, choose_student_clb.filter(action="back5"))

    dp.register_callback_query_handler(choose_student_data, choose_student_clb.filter(action="teacher_id"))
    dp.register_callback_query_handler(choose_student_data, choose_student_clb.filter(action="choose_back6"))

    dp.register_callback_query_handler(get_student_data, get_students_clb.filter(action="get_student_data"))
    dp.register_callback_query_handler(get_student_data, get_students_clb.filter(action="choose_back7"))

    dp.register_callback_query_handler(edit_lessons, get_students_clb.filter(action="edit_lessons"))
    dp.register_callback_query_handler(edit_lessons, get_students_clb.filter(action="choose_back8"))

    dp.register_callback_query_handler(less_or_more, student_lessons_confirm.filter(action="< 12_edit_"), IsAdmin())
    dp.register_callback_query_handler(less_or_more, student_lessons_confirm.filter(action="12_edit_"), IsAdmin())
    dp.register_callback_query_handler(less_or_more, student_lessons_confirm.filter(action="> 12_edit_"), IsAdmin())

    dp.register_callback_query_handler(edit_lessons_quantity, student_lessons_confirm.filter(action="edit_quantity"))











