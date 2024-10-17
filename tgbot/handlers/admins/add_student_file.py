from aiogram import Dispatcher
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.deep_linking import get_start_link

from tgbot.filters.is_admin import IsAdmin
from tgbot.handlers.admins.functions import get_types, get_subjects, get_days, get_times, get_teacher
from tgbot.keyboards.inline.catalog import admins_clb, student_custom_clb, add_student_clb


async def students_custom(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()

    markup = InlineKeyboardMarkup(row_width=2)
    markup.insert(InlineKeyboardButton(text="Добавить студента",
                                       callback_data=student_custom_clb.new(action="add", student_id="None")))
    markup.insert(InlineKeyboardButton(text="Удалить студента",
                                       callback_data=student_custom_clb.new(action="delete_student", student_id="None")))
    markup.insert(InlineKeyboardButton(text="Выбрать студента",
                                       callback_data=student_custom_clb.new(action="choose_student", student_id="None")))
    markup.row(InlineKeyboardButton(text="Назад", callback_data=admins_clb.new(action="back")))
    await call.bot.edit_message_text("Выберите действие:", call.from_user.id, call.message.message_id,
                                     reply_markup=markup)


# add / back1
async def add_student_types(call: CallbackQuery, callback_data: dict):
    await get_types(call, callback_data, add_student_clb, student_custom_clb)


# type_id / back2
async def add_student_subjects(call: CallbackQuery, callback_data: dict):
    await get_subjects(call, callback_data, add_student_clb)


# subject_id / back3
async def add_student_days(call: CallbackQuery, callback_data: dict):
    await get_days(call, callback_data, add_student_clb)


# day_id / back4
async def add_student_times(call: CallbackQuery, callback_data: dict):
    await get_times(call, callback_data, add_student_clb)


# time_id / back5
async def add_student_teacher(call: CallbackQuery, callback_data: dict):
    await get_teacher(call, callback_data, add_student_clb)


# teacher_id
async def add_student(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    type_id = int(callback_data.get("type_id"))
    subject_id = int(callback_data.get("subject_id"))
    day_id = int(callback_data.get("day_id"))
    time_id = int(callback_data.get("time_id"))
    teacher_id = int(callback_data.get("teacher_id"))

    subjects = await db.select_teacher_group(type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id, teacher_id=teacher_id)
    teacher_group_id = int(subjects.get("id"))
    deep_link = await db.add_deep_link(is_used=False)
    deep_link_id = deep_link.get("id")
    info = f"{teacher_group_id}:{deep_link_id}"
    student_link = await get_start_link(payload=info, encode=True)
    markup = InlineKeyboardMarkup(row_width=1)
    markup.insert(InlineKeyboardButton(text="⬅️ Назад", callback_data=add_student_clb.new(action="back5", type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id, teacher_id=0)))
    await call.bot.edit_message_text(f"Отправьте следующую ссылку студенту для студента\n {student_link} \n", call.from_user.id, call.message.message_id, reply_markup=markup)


def register_add_student_file(dp: Dispatcher):
    #                                                     IS_ADMIN_
    dp.register_callback_query_handler(students_custom, admins_clb.filter(action="students"), IsAdmin())
    dp.register_callback_query_handler(students_custom, student_custom_clb.filter(action="back"))
    # _______________________________________________________________________________________________________________
    dp.register_callback_query_handler(add_student_types, student_custom_clb.filter(action="add"))
    dp.register_callback_query_handler(add_student_types, add_student_clb.filter(action="back1"))

    dp.register_callback_query_handler(add_student_subjects, add_student_clb.filter(action="type_id"))
    dp.register_callback_query_handler(add_student_subjects, add_student_clb.filter(action="back2"))

    dp.register_callback_query_handler(add_student_days, add_student_clb.filter(action="subject_id"))
    dp.register_callback_query_handler(add_student_days, add_student_clb.filter(action="back3"))

    dp.register_callback_query_handler(add_student_times, add_student_clb.filter(action="day_id"))
    dp.register_callback_query_handler(add_student_times, add_student_clb.filter(action="back4"))

    dp.register_callback_query_handler(add_student_teacher, add_student_clb.filter(action="time_id"))
    dp.register_callback_query_handler(add_student_teacher, add_student_clb.filter(action="back5"))

    dp.register_callback_query_handler(add_student, add_student_clb.filter(action="teacher_id"))









