from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.handlers.admins.functions import get_teacher, get_times, get_days, get_subjects, get_types
from tgbot.keyboards.inline.catalog import groups_custom_clb, edit_group_clb, edit_smth_clb, edit_teacher_clb
from tgbot.states.users import Admins


# edit / back1
async def edit_group_types(call: CallbackQuery, callback_data: dict):
    await get_types(call, callback_data, edit_group_clb, groups_custom_clb)


# type_id / back2
async def edit_group_subjects(call: CallbackQuery, callback_data: dict):
    await get_subjects(call, callback_data, edit_group_clb)


# subject_id / back3
async def edit_group_days(call: CallbackQuery, callback_data: dict):
    await get_days(call, callback_data, edit_group_clb)


# day_id / back4
async def edit_group_times(call: CallbackQuery, callback_data: dict):
    await get_times(call, callback_data, edit_group_clb)


# time_id / back5
async def edit_group_teacher(call: CallbackQuery, callback_data: dict):
    await get_teacher(call, callback_data, edit_group_clb)


# teacher_id / back6
# Admins.Edit_group
async def group_edit(call: CallbackQuery, callback_data: dict, state: FSMContext):
    db = call.bot.get("db")
    await call.answer()
    await state.reset_state()
    try:
        teacher_group_id = int(callback_data.get("teacher_group_id"))
        subjects = await db.select_teacher_group(id=teacher_group_id)
        type_id = int(subjects.get("type_id"))
        subject_id = int(subjects.get("subject_id"))
        day_id = int(subjects.get("day_id"))
        time_id = int(subjects.get("time_id"))
        teacher_id = int(subjects.get("teacher_id"))
    except:
        type_id = int(callback_data.get("type_id"))
        subject_id = int(callback_data.get("subject_id"))
        day_id = int(callback_data.get("day_id"))
        time_id = int(callback_data.get("time_id"))
        teacher_id = int(callback_data.get("teacher_id"))
        subjects = await db.select_teacher_group(type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id, teacher_id=teacher_id)

    teacher_group_id = int(subjects.get("id"))
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
           f"Что именно вы желаете изменить?"
    markup = InlineKeyboardMarkup(row_width=1)

    markup.insert(InlineKeyboardButton(text="Тип курса", callback_data=edit_smth_clb.new(action="edit_type", teacher_group_id=teacher_group_id)))
    markup.insert(InlineKeyboardButton(text="Предмет", callback_data=edit_smth_clb.new(action="edit_subject", teacher_group_id=teacher_group_id)))
    markup.insert(InlineKeyboardButton(text="День", callback_data=edit_smth_clb.new(action="edit_day", teacher_group_id=teacher_group_id)))
    markup.insert(InlineKeyboardButton(text="Время", callback_data=edit_smth_clb.new(action="edit_time", teacher_group_id=teacher_group_id)))
    markup.insert(InlineKeyboardButton(text="Описание", callback_data=edit_smth_clb.new(action="edit_description", teacher_group_id=teacher_group_id)))
    markup.insert(InlineKeyboardButton(text="Учитель", callback_data=edit_smth_clb.new(action="edit_teacher", teacher_group_id=teacher_group_id)))

    markup.insert(InlineKeyboardButton(text="⬅️ Назад", callback_data=edit_group_clb.new(action="back5", type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id, teacher_id=teacher_id)))
    await call.bot.edit_message_text(text, call.from_user.id, call.message.message_id, reply_markup=markup)


# edit_teacher
async def group_edit_teacher(call: CallbackQuery, callback_data: dict, state: FSMContext):
    db = call.bot.get("db")
    await call.answer()
    teacher_group_id = int(callback_data.get("teacher_group_id"))
    action = callback_data.get("action")

    teachers = await db.select_all_teachers()
    markup = InlineKeyboardMarkup(row_width=1)
    for id, telegram_id, description in teachers:
        user = await db.select_user(telegram_id=telegram_id)
        full_name = user.get("full_name")
        markup.insert(InlineKeyboardButton(text=full_name, callback_data=edit_teacher_clb.new(action="teacher", teacher_id=id, teacher_group_id=teacher_group_id)))
    markup.insert(InlineKeyboardButton(text="Назад", callback_data=edit_teacher_clb.new(action="back", teacher_id="None", teacher_group_id=teacher_group_id)))
    await call.bot.edit_message_text("Выберите другого учителя на замену", call.from_user.id, call.message.message_id, reply_markup=markup)


async def group_edit_teacher_confirm(call: CallbackQuery, callback_data: dict, state: FSMContext):
    db = call.bot.get("db")
    await call.answer()
    teacher_id = int(callback_data.get("teacher_id"))
    teacher_group_id = int(callback_data.get("teacher_group_id"))

    await db.update_teacher_group(id=teacher_group_id, teacher_id=teacher_id)
    await call.bot.edit_message_text("Выберите успешно изменили учителя группы", call.from_user.id, call.message.message_id)


async def group_edit_step(call: CallbackQuery, callback_data: dict, state: FSMContext):
    db = call.bot.get("db")
    await call.answer()
    teacher_group_id = int(callback_data.get("teacher_group_id"))
    action = callback_data.get("action")

    markup = InlineKeyboardMarkup(row_width=1)
    markup.insert(InlineKeyboardButton(text="⬅️ Назад", callback_data=edit_smth_clb.new(action="back6", teacher_group_id=teacher_group_id)))

    await call.bot.send_message(call.from_user.id, "Отправьте изменнный текст")
    await Admins.Edit_group.set()
    await state.update_data(action=action)
    await state.update_data(teacher_group_id=teacher_group_id)


# Admins.Edit_group
async def group_edit_confirm(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    data = await state.get_data()
    action = data.get("action")
    teacher_group_id = int(data.get("teacher_group_id"))
    await state.reset_state()
    edited_text = message.text

    if action == "edit_type":
        await db.update_teacher_group(id=teacher_group_id, type=edited_text)
    elif action == "edit_subject":
        await db.update_teacher_group(id=teacher_group_id, subject=edited_text)
    elif action == "edit_day":
        await db.update_teacher_group(id=teacher_group_id, day=edited_text)
    elif action == "edit_time":
        await db.update_teacher_group(id=teacher_group_id, time=edited_text)
    elif action == "edit_description":
        await db.update_teacher_group(id=teacher_group_id, description=edited_text)
    else:
        pass

    await message.answer("Вы успешно изменили группу!")


def register_edit_group_file(dp: Dispatcher):
    #                                               IS_ADMIN_
    dp.register_callback_query_handler(edit_group_types, groups_custom_clb.filter(action="edit"))
    dp.register_callback_query_handler(edit_group_types, edit_group_clb.filter(action="back1"))

    dp.register_callback_query_handler(edit_group_subjects, edit_group_clb.filter(action="type_id"))
    dp.register_callback_query_handler(edit_group_subjects, edit_group_clb.filter(action="back2"))

    dp.register_callback_query_handler(edit_group_days, edit_group_clb.filter(action="subject_id"))
    dp.register_callback_query_handler(edit_group_days, edit_group_clb.filter(action="back3"))

    dp.register_callback_query_handler(edit_group_times, edit_group_clb.filter(action="day_id"))
    dp.register_callback_query_handler(edit_group_times, edit_group_clb.filter(action="back4"))

    dp.register_callback_query_handler(edit_group_teacher, edit_group_clb.filter(action="time_id"))
    dp.register_callback_query_handler(edit_group_teacher, edit_group_clb.filter(action="back5"))

    dp.register_callback_query_handler(group_edit, edit_group_clb.filter(action="teacher_id"))
    dp.register_callback_query_handler(group_edit, edit_teacher_clb.filter(action="back"))
    dp.register_callback_query_handler(group_edit, edit_smth_clb.filter(action="back6"), state=Admins.Edit_group)

    dp.register_callback_query_handler(group_edit_teacher, edit_smth_clb.filter(action="edit_teacher"))
    dp.register_callback_query_handler(group_edit_teacher_confirm, edit_teacher_clb.filter(action="teacher"))

    dp.register_callback_query_handler(group_edit_step, edit_smth_clb.filter())
    dp.register_message_handler(group_edit_confirm, state=Admins.Edit_group)








