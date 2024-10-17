from aiogram import Dispatcher
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.deep_linking import get_start_link

from tgbot.filters.is_admin import IsAdmin
from tgbot.keyboards.inline.catalog import teachers_custom_clb, admins_clb


async def teachers_custom(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()

    markup = InlineKeyboardMarkup(row_width=2)
    markup.insert(InlineKeyboardButton(text="Добавить учителя",
                                       callback_data=teachers_custom_clb.new(action="add", teacher_id="None")))
    markup.insert(InlineKeyboardButton(text="Удалить учителя",
                                       callback_data=teachers_custom_clb.new(action="delete", teacher_id="None")))
    markup.row(InlineKeyboardButton(text="Назад", callback_data=admins_clb.new(action="back")))
    await call.bot.edit_message_text("Выберите действие:", call.from_user.id, call.message.message_id,
                                     reply_markup=markup)


async def add_teacher(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()

    deep_link = await db.add_deep_link(is_used=False)
    deep_link_id = deep_link.get("id")
    info = f"teacher:{deep_link_id}"
    teacher_link = await get_start_link(payload=info, encode=True)
    markup = InlineKeyboardMarkup(row_width=1)
    markup.insert(InlineKeyboardButton(text="Назад", callback_data=teachers_custom_clb.new(action="back", teacher_id="None")))
    await call.bot.edit_message_text(f"Отправьте следующую ссылку учителю для регистрации {teacher_link} \n"
                                     f"Также учителю нужно будет написать небольшой текст о себе и своих навыках",
                                     call.from_user.id, call.message.message_id, reply_markup=markup)


def register_add_teacher_file(dp: Dispatcher):
    #                                               IS_ADMIN_
    dp.register_callback_query_handler(teachers_custom, admins_clb.filter(action="teachers"), IsAdmin())
    dp.register_callback_query_handler(teachers_custom, teachers_custom_clb.filter(action="back"))
    # _______________________________________________________________________________________________________________
    dp.register_callback_query_handler(add_teacher, teachers_custom_clb.filter(action="add"))








