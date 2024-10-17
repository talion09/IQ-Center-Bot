from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from tgbot.keyboards.inline.catalog import groups_custom_clb, student_custom_clb, teachers_custom_clb, admins_clb, teacher_clb


async def get_types(call: CallbackQuery, callback_data: dict, keyboard_clb: CallbackData, keyboard_clb_2: CallbackData = None):
    db = call.bot.get("db")
    await call.answer()
    all_subjects = await db.select_all_teacher_groups()
    markup = InlineKeyboardMarkup(row_width=1)
    unique_types = set()
    for id, type_id, type, subject_id, subject, description, day_id, day, time_id, time, teacher_id in all_subjects:
        if type not in unique_types:
            unique_types.add(type)
            markup.insert(InlineKeyboardButton(text=type, callback_data=keyboard_clb.new(action="type_id", type_id=type_id, subject_id=0, day_id=0, time_id=0, teacher_id=0)))

    if keyboard_clb_2 == groups_custom_clb:
        markup.insert(InlineKeyboardButton(text="Назад", callback_data=keyboard_clb_2.new(action="back", teacher_id="None", group_id="None")))
    elif keyboard_clb_2 == student_custom_clb:
        markup.insert(InlineKeyboardButton(text="Назад", callback_data=keyboard_clb_2.new(action="back", student_id="None")))
    elif keyboard_clb_2 == teachers_custom_clb:
        markup.insert(InlineKeyboardButton(text="Назад", callback_data=keyboard_clb_2.new(action="back", teacher_id="None")))
    elif keyboard_clb_2 == admins_clb:
        markup.insert(InlineKeyboardButton(text="Назад", callback_data=keyboard_clb_2.new(action="back")))
    else:
        pass
    await call.bot.edit_message_text("Выберите тип курса:", call.from_user.id, call.message.message_id, reply_markup=markup)


async def get_subjects(call: CallbackQuery, callback_data: dict, keyboard_clb: CallbackData):
    db = call.bot.get("db")
    await call.answer()
    type_id = int(callback_data.get("type_id"))

    all_subjects = await db.select_in_types(type_id=type_id)
    unique_subjects = set()
    markup = InlineKeyboardMarkup(row_width=1)
    for id, type_id, type, subject_id, subject, description, day_id, day, time_id, time, teacher_id in all_subjects:
        if subject not in unique_subjects:
            unique_subjects.add(subject)
            markup.insert(InlineKeyboardButton(text=subject, callback_data=keyboard_clb.new(action="subject_id", type_id=type_id, subject_id=subject_id, day_id=0, time_id=0, teacher_id=0)))
    markup.insert(InlineKeyboardButton(text="⬅️ Назад", callback_data=keyboard_clb.new(action="back1", type_id=type_id, subject_id=0, day_id=0, time_id=0, teacher_id=0)))
    await call.bot.edit_message_text("Выберите предмет:", call.from_user.id, call.message.message_id, reply_markup=markup)


async def get_days(call: CallbackQuery, callback_data: dict, keyboard_clb: CallbackData):
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
            markup.insert(InlineKeyboardButton(text=day, callback_data=keyboard_clb.new(action="day_id", type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=0, teacher_id=0)))
        if description not in lst_descrip:
            lst_descrip.append(description)
    text = f"{lst_descrip[0]}\n\nВыберите день:"
    markup.insert(InlineKeyboardButton(text="⬅️ Назад", callback_data=keyboard_clb.new(action="back2", type_id=type_id, subject_id=subject_id, day_id=0, time_id=0, teacher_id=0)))
    await call.bot.edit_message_text(text, call.from_user.id, call.message.message_id, reply_markup=markup)


async def get_times(call: CallbackQuery, callback_data: dict, keyboard_clb: CallbackData):
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
        markup.insert(InlineKeyboardButton(text=time,
                                           callback_data=keyboard_clb.new(action="time_id", type_id=type_id,
                                                                          subject_id=subject_id, day_id=day_id,
                                                                          time_id=time_id, teacher_id=0)))
    markup.insert(InlineKeyboardButton(text="⬅️ Назад", callback_data=keyboard_clb.new(action="back3", type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=0, teacher_id=0)))
    await call.bot.edit_message_text("Выберите время:", call.from_user.id, call.message.message_id, reply_markup=markup)


async def get_teacher(call: CallbackQuery, callback_data: dict, keyboard_clb: CallbackData):
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
            telegram_id = int(teacher.get("telegram_id"))
            user = await db.select_user(telegram_id=telegram_id)
            full_name = user.get("full_name")
            markup.insert(InlineKeyboardButton(text=full_name, callback_data=keyboard_clb.new(action="teacher_id", type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id, teacher_id=teacher_id)))
    markup.insert(InlineKeyboardButton(text="⬅️ Назад", callback_data=keyboard_clb.new(action="back4", type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id, teacher_id=0)))
    await call.bot.edit_message_text("Выберите учителя:", call.from_user.id, call.message.message_id, reply_markup=markup)


# teacher_id / back6
async def group_edit(call: CallbackQuery, callback_data: dict, keyboard_clb: CallbackData, state: FSMContext):
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
    markup.insert(InlineKeyboardButton(text="⬅️ Назад", callback_data=keyboard_clb.new(action="back5", type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id, teacher_id=teacher_id)))
    await call.bot.edit_message_text(text, call.from_user.id, call.message.message_id, reply_markup=markup)








