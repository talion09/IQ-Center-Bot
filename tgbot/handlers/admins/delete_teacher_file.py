from aiogram import Dispatcher
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from tgbot.keyboards.inline.catalog import teachers_custom_clb


async def delete_teacher(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()

    teachers = await db.select_all_teachers()
    markup = InlineKeyboardMarkup(row_width=1)
    for id, telegram_id, description in teachers:
        user = await db.select_user(telegram_id=telegram_id)
        full_name = user.get("full_name")
        markup.insert(InlineKeyboardButton(text=f"❌ {full_name}",
                                           callback_data=teachers_custom_clb.new(action="delete_teacher",
                                                                                 teacher_id=id)))
    markup.insert(
        InlineKeyboardButton(text="Назад", callback_data=teachers_custom_clb.new(action="back", teacher_id="None")))
    await call.bot.edit_message_text(f"При удалении учителя удалятся и Предметы и Группы с ученками, "
                                     f"которые он введет. Если хотите, чтобы этого не происходило нужно "
                                     f"изменить учителя группы в разделе 'Группы'",
                                     call.from_user.id, call.message.message_id, reply_markup=markup)


async def delete_teacher_question(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    teacher_id = int(callback_data.get("teacher_id"))

    teacher = await db.select_teacher(id=teacher_id)
    telegram_id = int(teacher.get("telegram_id"))
    user = await db.select_user(telegram_id=telegram_id)
    full_name = user.get("full_name")

    markup = InlineKeyboardMarkup(row_width=1)
    markup.insert(InlineKeyboardButton(text=f"Да, удалить",
                                       callback_data=teachers_custom_clb.new(action="delete_teacher_confirm",
                                                                             teacher_id=teacher_id)))
    markup.insert(InlineKeyboardButton(text="Назад",
                                       callback_data=teachers_custom_clb.new(action="back_2", teacher_id=teacher_id)))
    await call.bot.edit_message_text(f"Вы уверены, что хотите удалить учителя <b>{full_name}</b> ?", call.from_user.id,
                                     call.message.message_id, reply_markup=markup)


async def delete_teacher_confirm(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    teacher_id = int(callback_data.get("teacher_id"))

    teacher_groups = await db.select_ids_in_teachers(teacher_id=teacher_id)
    all_id_groups = []
    for id in teacher_groups:
        ids = await db.select_id_groups(teacher_group_id=int(id.get("id")))
        for group_id in ids:
            all_id_groups.append(int(group_id.get("id")))
    for group_id in all_id_groups:
        await db.delete_group(id=group_id)
    for teacher_group_id in teacher_groups:
        ids = await db.select_id_attendance_record(teacher_group_id=int(teacher_group_id.get("id")))
        for id in ids:
            await db.delete_attendance_record(id=int(id.get("id")))
        await db.delete_teacher_group(id=int(teacher_group_id.get("id")))

    await db.delete_teacher(id=teacher_id)
    await call.bot.edit_message_text(f"Учитель, предметы и группы связанные с ним успешно удалены", call.from_user.id,
                                     call.message.message_id)


def register_delete_teacher_file(dp: Dispatcher):
    #                                               IS_ADMIN_
    dp.register_callback_query_handler(delete_teacher, teachers_custom_clb.filter(action="delete"))
    dp.register_callback_query_handler(delete_teacher, teachers_custom_clb.filter(action="back_2"))
    dp.register_callback_query_handler(delete_teacher_question, teachers_custom_clb.filter(action="delete_teacher"))
    dp.register_callback_query_handler(delete_teacher_confirm, teachers_custom_clb.filter(action="delete_teacher_confirm"))








