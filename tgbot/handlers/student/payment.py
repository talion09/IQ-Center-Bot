from aiogram import Dispatcher
from aiogram import types
import datetime

from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, \
    CallbackQuery, LabeledPrice

from tgbot.filters.is_admin import IsStudent
from tgbot.handlers.users.start import bot_start, suitable_menu
from tgbot.keyboards.inline.catalog import pay_clb
from tgbot.misc.items import Item


async def get_groups(message: types.Message):
    db = message.bot.get("db")
    student = await db.select_student(telegram_id=message.from_user.id)
    remaining_lessons = int(student.get("remaining_lessons"))
    student_id = int(student.get("id"))
    # student_id = 51

    teacher_groups = await db.select_groups2(student_id=student_id)

    markup = InlineKeyboardMarkup()

    for teacher_group_id in teacher_groups:
        teacher_group = await db.select_teacher_group(id=int(teacher_group_id.get("teacher_group_id")))
        subject = teacher_group.get("subject")
        day = teacher_group.get("day")
        time = teacher_group.get("time")

        text_button = f"{subject} ({day} {time})"
        markup.insert(InlineKeyboardButton(text=text_button, callback_data=pay_clb.new(student_id=student_id, teacher_group_id=int(teacher_group_id.get("teacher_group_id")))))

    text = f"За какую группу хотите заплатить?"
    await message.answer(text, reply_markup=markup)


async def pay_group(call: CallbackQuery, callback_data: dict):
    db = call.bot.get("db")
    await call.answer()
    student_id = int(callback_data.get("student_id"))
    teacher_group_id = int(callback_data.get("teacher_group_id"))

    teacher_group = await db.select_teacher_group(id=teacher_group_id)
    type = teacher_group.get("type")
    subject = teacher_group.get("subject")
    day = teacher_group.get("day")
    time = teacher_group.get("time")
    teacher_id = int(teacher_group.get("teacher_id"))

    teacher = await db.select_teacher(id=teacher_id)
    teacher_telegram_id = teacher.get("telegram_id")
    user = await db.select_user(telegram_id=teacher_telegram_id)
    teacher_name = user.get("full_name")

    user = await db.select_user(telegram_id=call.from_user.id)
    student_name = user.get("full_name")
    phone = user.get("phone")

    text1 = f"Тип курса: {type} \n\n" \
            f"Предмет: {subject} \n\n" \
            f"Когда: {day} в {time} \n\n" \
            f"Учитель: {teacher_name}\n\n\n" \
            f"Имя и Фамилие: {student_name} \n\n" \
            f"Телефонный номер: {phone}\n\n\n" \
            f"Все верно?"
    # markup = InlineKeyboardMarkup(row_width=1)
    # markup.insert(InlineKeyboardButton(text="Оплатить", callback_data=sign_up_clb.new(action="confirm_send", type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id)))
    # markup.insert(InlineKeyboardButton(text="⬅️ Назад", callback_data=sign_up_clb.new(action="back", type_id=type_id, subject_id=subject_id, day_id=day_id, time_id=time_id)))

    sums_amount = 820000 * 100
    Payment_ready = Item(
        title="Ваша Оплата",
        description=text1,
        currency="UZS",
        prices=[LabeledPrice(label="Оплата", amount=sums_amount)],
        start_parameter="Payment"
    )
    await call.bot.send_invoice(call.from_user.id, **Payment_ready.generate_invoice(), payload="123456")


async def process_pre_checkout_query(query: types.PreCheckoutQuery, state: FSMContext):
    db = query.bot.get('db')
    await query.bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=True)
    user_in_db = await db.select_user(telegram_id=int(query.from_user.id))
    full_name = user_in_db.get("full_name")
    menu = await suitable_menu(query)

    student = await db.select_student(telegram_id=int(query.from_user.id))
    student_id = int(student.get("id"))
    remaining_lessons = int(student.get("remaining_lessons"))
    await db.update_student(id=student_id, remaining_lessons=(remaining_lessons + 12))
    await query.bot.send_message(chat_id=query.from_user.id, text=f"{full_name}, Спасибо что выбираете IQ Center!", reply_markup=menu)


def register_payment(dp: Dispatcher):
    # dp.register_message_handler(get_groups, IsStudent(), text="⚖️ Оплатить")
    dp.register_message_handler(get_groups, text="⚖️ Оплатить")
    dp.register_callback_query_handler(pay_group, pay_clb.filter())
    dp.register_pre_checkout_query_handler(process_pre_checkout_query)

