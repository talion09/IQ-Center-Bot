from aiogram import Dispatcher
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.handlers.admins.functions import get_types, get_subjects, get_days, get_times, get_teacher
from tgbot.keyboards.inline.catalog import groups_custom_clb, delete_group_clb


# delete / back1
async def delete_group_types(call: CallbackQuery, callback_data: dict):
    await get_types(call, callback_data, delete_group_clb, groups_custom_clb)


# type_id / back2
async def delete_group_subjects(call: CallbackQuery, callback_data: dict):
    await get_subjects(call, callback_data, delete_group_clb)


# subject_id / back3
async def delete_group_days(call: CallbackQuery, callback_data: dict):
    await get_days(call, callback_data, delete_group_clb)


# day_id / back4
async def delete_group_times(call: CallbackQuery, callback_data: dict):
    await get_times(call, callback_data, delete_group_clb)


# time_id / back5
async def delete_group_teacher(call: CallbackQuery, callback_data: dict):
    await get_teacher(call, callback_data, delete_group_clb)


# teacher_id / back6
async def group_delete(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    type_id = int(callback_data.get("type_id"))
    subject_id = int(callback_data.get("subject_id"))
    day_id = int(callback_data.get("day_id"))
    time_id = int(callback_data.get("time_id"))
    teacher_id = int(callback_data.get("teacher_id"))

    subjects = await db.select_teacher_group(type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id, teacher_id=teacher_id)

    type = subjects.get("type")
    subject = subjects.get("subject")
    day = subjects.get("day")
    time = subjects.get("time")
    description = subjects.get("description")

    teacher = await db.select_teacher(id=teacher_id)
    telegram_id = int(teacher.get("telegram_id"))
    teacher_description = teacher.get("description")

    teacher_user = await db.select_user(telegram_id=telegram_id)
    full_name = teacher_user.get("full_name")

    text = f"<b>Тип курса:</b> {type} \n" \
           f"<b>Предмет:</b> {subject} \n{description}\n" \
           f"<b>Когда:</b> {day} в {time} \n" \
           f"<b>Учитель:</b> {full_name}\n{teacher_description}\n\n" \
           f"Удалить этот предмет?\n\n" \
           f"<b>Важно! С удалением предмета удалятся и группы с учениками, которые ходят на этот предмет!</b>"
    markup = InlineKeyboardMarkup(row_width=1)
    markup.insert(InlineKeyboardButton(text="Да, удалить", callback_data=delete_group_clb.new(action="confirm_delete", type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id, teacher_id=teacher_id)))
    markup.insert(InlineKeyboardButton(text="⬅️ Назад", callback_data=delete_group_clb.new(action="back5", type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id, teacher_id=teacher_id)))
    await call.bot.edit_message_text(text, call.from_user.id, call.message.message_id, reply_markup=markup)


# confirm_delete
async def group_delete_confirm(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    type_id = int(callback_data.get("type_id"))
    subject_id = int(callback_data.get("subject_id"))
    day_id = int(callback_data.get("day_id"))
    time_id = int(callback_data.get("time_id"))
    teacher_id = int(callback_data.get("teacher_id"))

    subjects = await db.select_teacher_group(type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id, teacher_id=teacher_id)
    teacher_group_id = int(subjects.get("id"))
    groups_id = await db.select_id_groups(teacher_group_id=teacher_group_id)
    for id_group in groups_id:
        await db.delete_group(id=int(id_group.get("id")))

    attendances = await db.select_attendances_4(teacher_group_id=teacher_group_id)
    if len(attendances) != 0:
        for attendance in attendances:
            attendance_id = int(attendance.get("id"))
            await db.delete_attendance_record(id=attendance_id)

    await db.delete_teacher_group(id=int(teacher_group_id))
    text = f"Предмет и группа с учениками удалена успешно!"
    await call.bot.edit_message_text(text, call.from_user.id, call.message.message_id)


def register_delete_group_file(dp: Dispatcher):
    #                                               IS_ADMIN_
    dp.register_callback_query_handler(delete_group_types, groups_custom_clb.filter(action="delete"))
    dp.register_callback_query_handler(delete_group_types, delete_group_clb.filter(action="back1"))

    dp.register_callback_query_handler(delete_group_subjects, delete_group_clb.filter(action="type_id"))
    dp.register_callback_query_handler(delete_group_subjects, delete_group_clb.filter(action="back2"))

    dp.register_callback_query_handler(delete_group_days, delete_group_clb.filter(action="subject_id"))
    dp.register_callback_query_handler(delete_group_days, delete_group_clb.filter(action="back3"))

    dp.register_callback_query_handler(delete_group_times, delete_group_clb.filter(action="day_id"))
    dp.register_callback_query_handler(delete_group_times, delete_group_clb.filter(action="back4"))

    dp.register_callback_query_handler(delete_group_teacher, delete_group_clb.filter(action="time_id"))
    dp.register_callback_query_handler(delete_group_teacher, delete_group_clb.filter(action="back5"))

    dp.register_callback_query_handler(group_delete, delete_group_clb.filter(action="teacher_id"))
    dp.register_callback_query_handler(group_delete, delete_group_clb.filter(action="back6"))

    dp.register_callback_query_handler(group_delete_confirm, delete_group_clb.filter(action="confirm_delete"))







