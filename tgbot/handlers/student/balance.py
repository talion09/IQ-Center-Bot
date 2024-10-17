from aiogram import Dispatcher
from aiogram import types
import datetime


async def get_balance(message: types.Message):
    db = message.bot.get("db")
    student = await db.select_student(telegram_id=message.from_user.id)
    remaining_lessons = int(student.get("remaining_lessons"))
    student_id = int(student.get("id"))

    calculation = 820000 / 12 * remaining_lessons

    teacher_groups = await db.select_groups2(student_id=student_id)
    subjects = f""
    for id_teacher_group in teacher_groups:
        teacher_group = await db.select_teacher_group(id=int(id_teacher_group.get("teacher_group_id")))
        subject = teacher_group.get("subject")
        subjects += f"{subject}\n"

    text = f"Ваш баланс: {int(calculation)} сум\n" \
           f"Предметы: \n{subjects}\n" \
           f"Пропущенные уроки за последние 2 месяца:\n"

    current_date = datetime.date.today()
    # Расчет даты два месяца назад
    two_months_ago = current_date - datetime.timedelta(days=60)

    skips = await db.select_skips_for_student_in_last_two_months(student_id, two_months_ago)
    for id, student_id, lesson_date in skips:
        date_string = lesson_date.strftime('%Y-%m-%d')
        text += f"{date_string} \n"

    text += f"\nОценки за последние 2 месяца:\n"
    attendance_marks = await db.select_marks_for_student_in_last_two_months(student_id, two_months_ago)
    for id, teacher_group_id, student_id, lesson_date, attendance, marks in attendance_marks:
        if marks is not None:
            date_string = lesson_date.strftime('%Y-%m-%d')
            text += f"{date_string} - {marks}\n"
    await message.answer(text)


def register_balance(dp: Dispatcher):
    # dp.register_message_handler(get_balance, IsStudent(), text="💳 Баланс")
    dp.register_message_handler(get_balance, text="💳 Баланс")













