import re

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, CallbackQuery, InlineKeyboardMarkup, \
    InlineKeyboardButton, ReplyKeyboardRemove

from tgbot.filters.is_admin import IsAdmin
from tgbot.keyboards.inline.catalog import admins_clb, groups_custom_clb
from tgbot.states.users import Admins


async def groups_custom(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()

    markup = InlineKeyboardMarkup(row_width=2)
    markup.insert(InlineKeyboardButton(text="Добавить группу",
                                       callback_data=groups_custom_clb.new(action="add", teacher_id="None",
                                                                           group_id="None")))
    markup.insert(InlineKeyboardButton(text="Удалить группу",
                                       callback_data=groups_custom_clb.new(action="delete", teacher_id="None",
                                                                           group_id="None")))
    markup.insert(InlineKeyboardButton(text="Изменить группу",
                                       callback_data=groups_custom_clb.new(action="edit", teacher_id="None",
                                                                           group_id="None")))
    markup.row(InlineKeyboardButton(text="Назад", callback_data=admins_clb.new(action="back")))
    await call.bot.edit_message_text("Выберите действие:", call.from_user.id, call.message.message_id,
                                     reply_markup=markup)


async def add_group(call: CallbackQuery, callback_data: dict, state: FSMContext):
    db = call.bot.get("db")
    await call.answer()
    await state.reset_state()

    teachers = await db.select_all_teachers()
    markup = InlineKeyboardMarkup(row_width=1)
    for id, telegram_id, description in teachers:
        user = await db.select_user(telegram_id=telegram_id)
        full_name = user.get("full_name")
        markup.insert(InlineKeyboardButton(text=f"{full_name}",
                                           callback_data=groups_custom_clb.new(action="link_teacher", teacher_id=id,
                                                                               group_id="None")))
    markup.insert(
        InlineKeyboardButton(text="Назад",
                             callback_data=groups_custom_clb.new(action="back", teacher_id="None", group_id="None")))
    await call.bot.edit_message_text(f"Какой учитель будет вести эту группу?",
                                     call.from_user.id, call.message.message_id, reply_markup=markup)


async def link_teacher(call: CallbackQuery, callback_data: dict, state: FSMContext):
    db = call.bot.get("db")
    await call.answer()
    teacher_id = int(callback_data.get("teacher_id"))
    group_id = callback_data.get("teacher_id")

    teacher = await db.select_teacher(id=teacher_id)
    telegram_id = int(teacher.get("telegram_id"))
    user = await db.select_user(telegram_id=telegram_id)
    full_name = user.get("full_name")

    markup = InlineKeyboardMarkup(row_width=1)
    text = f"Вы выбрали учителя <b>{full_name}</b>\n" \
           f"Теперь вам нужно отправить сообщение строго в следующем формате. \n" \
           f"Пример:\n\n\n" \
           f"<b>Тип курса: <code>|Подготовительные|</code></b>\n" \
           f"<b>Предмет: <code>|Математика|</code></b>\n" \
           f"<b>Дни проведения: <code>|Пн-Ср-Пт|</code></b>\n" \
           f"<b>Время проведения: <code>|10:30 - 11:50|</code></b>\n"
    markup.insert(InlineKeyboardButton(text="Назад",
                                       callback_data=groups_custom_clb.new(action="back_2", teacher_id=teacher_id,
                                                                           group_id="None")))
    await call.bot.edit_message_text(text, call.from_user.id, call.message.message_id, reply_markup=markup)
    await Admins.Add_group.set()
    await state.update_data(teacher_id=teacher_id)


# Admins.Add_group
async def get_text_with_data(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    data = await state.get_data()
    teacher_id = int(data.get("teacher_id"))
    teacher = await db.select_teacher(id=teacher_id)
    telegram_id = int(teacher.get("telegram_id"))
    user = await db.select_user(telegram_id=telegram_id)
    full_name = user.get("full_name")
    text = message.text
    matches = re.findall(r'\|([^|]+)\|', text)

    type = await db.select_teacher_group(type=matches[0])
    subject = await db.select_teacher_group(subject=matches[1])
    day = await db.select_teacher_group(day=matches[2])
    time = await db.select_teacher_group(time=matches[3])

    count = int()

    try:
        type_id = type.get("type_id")
    except:
        max_type_id = await db.get_max_type_id()
        type_id = int(max_type_id) + 1
        count += 1

    try:
        subject_id = subject.get("subject_id")
    except:
        max_subject_id = await db.get_max_subject_id()
        subject_id = int(max_subject_id) + 1
        count += 1

    try:
        day_id = day.get("day_id")
    except:
        max_day_id = await db.get_max_day_id()
        day_id = int(max_day_id) + 1

    try:
        time_id = time.get("time_id")
    except:
        max_time_id = await db.get_max_time_id()
        time_id = int(max_time_id) + 1

    if count >= 1:
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(KeyboardButton(text="Отменить"))
        await message.answer("Отправьте небольшой текст об этом предмете", reply_markup=markup)
        await Admins.New_description.set()
        await state.update_data(type=matches[0])
        await state.update_data(subject=matches[1])
        await state.update_data(day=matches[2])
        await state.update_data(time=matches[3])
        await state.update_data(type_id=type_id)
        await state.update_data(subject_id=subject_id)
        await state.update_data(day_id=day_id)
        await state.update_data(time_id=time_id)
    else:
        obj = await db.select_in_subjects_row(type_id=type_id, subject_id=subject_id)
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(KeyboardButton(text="Да ✅"))
        markup.add(KeyboardButton(text="Отменить"))
        descrip = obj.get("description")
        text1 = f"Тип курса: {matches[0]} \n" \
                f"Предмет: {matches[1]} \n" \
                f"Когда: {matches[2]} в {matches[3]} \n\n" \
                f"Описание: {descrip}\n\n" \
                f"Учитель: {full_name}\n\n" \
                f"Все верно?"
        await message.answer(text1, reply_markup=markup)
        await Admins.New_group.set()
        await state.update_data(type=matches[0])
        await state.update_data(subject=matches[1])
        await state.update_data(day=matches[2])
        await state.update_data(time=matches[3])
        await state.update_data(description=descrip)
        await state.update_data(type_id=type_id)
        await state.update_data(subject_id=subject_id)
        await state.update_data(day_id=day_id)
        await state.update_data(time_id=time_id)


# Admins.New_group
async def new_group_confirm(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    data = await state.get_data()
    teacher_id = int(data.get("teacher_id"))
    type = data.get("type")
    subject = data.get("subject")
    day = data.get("day")
    time = data.get("time")
    description = data.get("description")
    type_id = data.get("type_id")
    subject_id = data.get("subject_id")
    day_id = data.get("day_id")
    time_id = data.get("time_id")

    await db.add_teacher_group(type_id, type, subject_id, subject, description, day_id, day, time_id, time, teacher_id)
    await message.answer("Группы с учителем успешно созданы!", reply_markup=ReplyKeyboardRemove())


# Admins.New_description
async def new_description(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    data = await state.get_data()
    teacher_id = int(data.get("teacher_id"))
    type = data.get("type")
    subject = data.get("subject")
    day = data.get("day")
    time = data.get("time")
    description = message.text
    type_id = data.get("type_id")
    subject_id = data.get("subject_id")
    day_id = data.get("day_id")
    time_id = data.get("time_id")

    teacher = await db.select_teacher(id=teacher_id)
    telegram_id = int(teacher.get("telegram_id"))
    user = await db.select_user(telegram_id=telegram_id)
    full_name = user.get("full_name")

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(text="Да ✅"))
    markup.add(KeyboardButton(text="Отменить"))
    text1 = f"Тип курса: {type} \n" \
            f"Предмет: {subject} \n" \
            f"Когда: {day} в {time} \n\n" \
            f"Описание: {description}\n\n" \
            f"Учитель: {full_name}\n\n" \
            f"Все верно?"
    await message.answer(text1, reply_markup=markup)
    await Admins.New_group.set()
    await state.update_data(description=description)
    await state.update_data(type_id=type_id)
    await state.update_data(subject_id=subject_id)
    await state.update_data(day_id=day_id)
    await state.update_data(time_id=time_id)


def register_add_group_file(dp: Dispatcher):
    #                                               IS_ADMIN_
    dp.register_callback_query_handler(groups_custom, admins_clb.filter(action="groups"), IsAdmin())
    dp.register_callback_query_handler(groups_custom, groups_custom_clb.filter(action="back"))
    # _______________________________________________________________________________________________________________
    dp.register_callback_query_handler(add_group, groups_custom_clb.filter(action="back_2"), state=Admins.Add_group)
    dp.register_callback_query_handler(add_group, groups_custom_clb.filter(action="add"))

    dp.register_callback_query_handler(link_teacher, groups_custom_clb.filter(action="link_teacher"))

    dp.register_message_handler(get_text_with_data, state=Admins.Add_group)
    dp.register_message_handler(new_group_confirm, state=Admins.New_group, text="Да ✅")
    dp.register_message_handler(new_description, state=Admins.New_description)







