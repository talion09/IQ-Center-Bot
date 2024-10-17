from aiogram import Dispatcher
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.handlers.admins.functions import get_teacher, get_times, get_days, get_subjects, get_types
from tgbot.keyboards.inline.catalog import delete_student_clb, get_students_clb, student_custom_clb, add_student_clb


# delete / back1
async def delete_students_types(call: CallbackQuery, callback_data: dict):
    await get_types(call, callback_data, delete_student_clb, student_custom_clb)


# type_id / back2
async def delete_students_subjects(call: CallbackQuery, callback_data: dict):
    await get_subjects(call, callback_data, delete_student_clb)


# subject_id / back3
async def delete_students_days(call: CallbackQuery, callback_data: dict):
    await get_days(call, callback_data, delete_student_clb)


# day_id / back4
async def delete_students_times(call: CallbackQuery, callback_data: dict):
    await get_times(call, callback_data, delete_student_clb)


# time_id / back5
async def delete_students_teacher(call: CallbackQuery, callback_data: dict):
    await get_teacher(call, callback_data, delete_student_clb)


# teacher_id / back6
async def delete_students_students(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    type_id = int(callback_data.get("type_id"))
    subject_id = int(callback_data.get("subject_id"))
    day_id = int(callback_data.get("day_id"))
    time_id = int(callback_data.get("time_id"))
    teacher_id = int(callback_data.get("teacher_id"))

    subjects = await db.select_teacher_group(type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id, teacher_id=teacher_id)
    teacher_group_id = int(subjects.get("id"))

    text = f"Выберите студента, которого хотите удалить"
    markup = InlineKeyboardMarkup(row_width=1)
    groups_id = await db.select_id_groups(teacher_group_id=teacher_group_id)
    for id in groups_id:
        group = await db.select_group(id=int(id.get("id")))
        student_id = int(group.get("student_id"))
        student = await db.select_student(id=student_id)
        telegram_id = int(student.get("telegram_id"))
        user = await db.select_user(telegram_id=telegram_id)
        full_name =  user.get("full_name")
        markup.insert(InlineKeyboardButton(text=full_name, callback_data=get_students_clb.new(action="get_student", teacher_group_id=teacher_group_id, student_id=student_id)))
    markup.insert(InlineKeyboardButton(text="⬅️ Назад", callback_data=delete_student_clb.new(action="back5", type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id, teacher_id=teacher_id)))
    await call.bot.edit_message_text(text, call.from_user.id, call.message.message_id, reply_markup=markup)


# get_student
async def get_student_handler(call: CallbackQuery, callback_data: dict):
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
    remaining_lessons = int(student.get("remaining_lessons"))
    calculation = 820000 / 12 * remaining_lessons
    text = f"Студент: {full_name}\n" \
           f"Предметы: \n{subjects}\n" \
           f"Баланс: {calculation}\n\n" \
           f"Вы уверены что хотите удалить студента из этой группы??"
    markup = InlineKeyboardMarkup(row_width=1)
    markup.insert(InlineKeyboardButton(text="Да, удалить", callback_data=get_students_clb.new(action="confirm",
                                                                                          teacher_group_id=teacher_group_id,
                                                                                          student_id=student_id)))
    markup.insert(InlineKeyboardButton(text="⬅️ Назад", callback_data=get_students_clb.new(action="back6",
                                                                                          teacher_group_id=teacher_group_id,
                                                                                          student_id=student_id)))
    await call.bot.edit_message_text(text, call.from_user.id, call.message.message_id, reply_markup=markup)


# confirm
async def get_student_handler_confirm(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    teacher_group_id = int(callback_data.get("teacher_group_id"))
    student_id = int(callback_data.get("student_id"))

    group = await db.select_group(teacher_group_id=teacher_group_id, student_id=student_id)
    group_id = int(group.get("id"))
    await db.delete_group(id=group_id)

    # group_ids = await db.select_groups3(student_id=student_id)
    # for group in group_ids:
    #     group_id = int(group.get("id"))
    #     await db.delete_group(id=group_id)
    #
    # attendances = await db.select_attendances_3(student_id=student_id)
    # if len(attendances) != 0:
    #     for attendance in attendances:
    #         attendance_id = int(attendance.get("id"))
    #         await db.delete_attendance_record(id=attendance_id)
    #
    # skips = await db.select_skips_3(student_id=student_id)
    # if len(skips) != 0:
    #     for skip in skips:
    #         skip_id = int(skip.get("id"))
    #         await db.delete_skip2(id=skip_id)
    #
    # await db.delete_student(id=student_id)

    text = f"Вы успешно удалили студента из этой группы"
    await call.bot.edit_message_text(text, call.from_user.id, call.message.message_id)


def register_delete_student_file(dp: Dispatcher):
    #                                               IS_ADMIN_
    dp.register_callback_query_handler(delete_students_types, student_custom_clb.filter(action="delete_student"))
    dp.register_callback_query_handler(delete_students_types, delete_student_clb.filter(action="back1"))

    dp.register_callback_query_handler(delete_students_subjects, delete_student_clb.filter(action="type_id"))
    dp.register_callback_query_handler(delete_students_subjects, delete_student_clb.filter(action="back2"))

    dp.register_callback_query_handler(delete_students_days, delete_student_clb.filter(action="subject_id"))
    dp.register_callback_query_handler(delete_students_days, delete_student_clb.filter(action="back3"))

    dp.register_callback_query_handler(delete_students_times, delete_student_clb.filter(action="day_id"))
    dp.register_callback_query_handler(delete_students_times, delete_student_clb.filter(action="back4"))

    dp.register_callback_query_handler(delete_students_teacher, delete_student_clb.filter(action="time_id"))
    dp.register_callback_query_handler(delete_students_teacher, delete_student_clb.filter(action="back5"))

    dp.register_callback_query_handler(delete_students_students, delete_student_clb.filter(action="teacher_id"))
    dp.register_callback_query_handler(delete_students_students, get_students_clb.filter(action="back6"))

    dp.register_callback_query_handler(get_student_handler, get_students_clb.filter(action="get_student"))

    dp.register_callback_query_handler(get_student_handler_confirm, get_students_clb.filter(action="confirm"))








