from aiogram.types import Message
from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


class IsAdmin(BoundFilter):
    async def check(self, message: Message):
        db = message.bot.get('db')
        admins_list = []
        for id, telegram_id, name in await db.select_all_admins():
            admins_list.append(telegram_id)
        return message.from_user.id in admins_list


class IsTeacher(BoundFilter):
    async def check(self, message: Message):
        db = message.bot.get('db')
        teachers_list = []
        for id, telegram_id, description in await db.select_all_teachers():
            teachers_list.append(telegram_id)
        return message.from_user.id in teachers_list


class IsStudent(BoundFilter):
    async def check(self, message: Message):
        db = message.bot.get('db')
        student_list = []
        for id, telegram_id, registration_date, remaining_lessons in await db.select_all_students():
            student_list.append(telegram_id)
        return message.from_user.id in student_list




