import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from tgbot.db_api.postgresql import Database
from tgbot.config import load_config
from tgbot.filters.is_admin import IsAdmin, IsTeacher, IsStudent
from tgbot.handlers.admins.add_group_file import register_add_group_file
from tgbot.handlers.admins.add_student_file import register_add_student_file
from tgbot.handlers.admins.add_teacher_file import register_add_teacher_file
from tgbot.handlers.admins.administration import register_administration
from tgbot.handlers.admins.choose_student_file import register_choose_student_file
from tgbot.handlers.admins.debtors import register_debtors
from tgbot.handlers.admins.delete_group_file import register_delete_group_file
from tgbot.handlers.admins.delete_student_file import register_delete_student_file
from tgbot.handlers.admins.delete_teacher_file import register_delete_teacher_file
from tgbot.handlers.admins.edit_group_file import register_edit_group_file
from tgbot.handlers.student.balance import register_balance
from tgbot.handlers.student.payment import register_payment
from tgbot.handlers.teacher.marks import register_marks
from tgbot.handlers.teacher.teacher_descrip import register_teacher_descrip
from tgbot.handlers.teacher.teacher_groups import register_teacher_groups
from tgbot.handlers.users.about import register_about
from tgbot.handlers.users.custom import register_custom
from tgbot.handlers.users.info_user import register_info_user
from tgbot.handlers.users.private_office import register_private_office
from tgbot.handlers.users.sign_up import register_sign_up
from tgbot.handlers.users.start import register_start
from tgbot.handlers.users.subjects import register_subjects
from tgbot.handlers.users.teachers import register_teachers
from tgbot.misc.notify_admins import on_startup_notify
from tgbot.misc.set_bot_commands import set_default_commands

logger = logging.getLogger(__name__)


def register_all_filters(dp):
    dp.filters_factory.bind(IsAdmin)
    dp.filters_factory.bind(IsTeacher)
    dp.filters_factory.bind(IsStudent)


def register_all_handlers(dp):
    register_start(dp)
    register_info_user(dp)
    register_subjects(dp)
    register_teachers(dp)
    register_sign_up(dp)
    register_teacher_groups(dp)
    register_teacher_descrip(dp)
    register_about(dp)
    register_custom(dp)
    register_private_office(dp)
    register_balance(dp)
    register_payment(dp)

    register_add_group_file(dp)
    register_add_teacher_file(dp)
    register_add_student_file(dp)
    register_administration(dp)
    register_delete_teacher_file(dp)
    register_delete_student_file(dp)
    register_choose_student_file(dp)
    register_delete_group_file(dp)
    register_edit_group_file(dp)
    register_debtors(dp)
    register_marks(dp)


async def main():
    config = load_config(".env")

    storage = MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(bot, storage=storage)
    db = Database()

    bot['config'] = config

    register_all_filters(dp)
    register_all_handlers(dp)

    await db.create()

    # await db.drop_attendance()
    # await db.drop_skip()
    # await db.drop_groups()
    # await db.drop_teacher_group()
    # await db.drop_teachers()
    # await db.drop_students()
    # await db.drop_admins()
    # await db.drop_users()
    # await db.drop_deep_link()

    await db.create_table_users()
    await db.create_table_admins()
    await db.create_table_students()
    await db.create_table_skips()
    await db.create_table_teachers()
    await db.create_table_teacher_group()
    await db.create_table_groups()
    await db.create_table_attendance()
    await db.create_table_deep_links()

    bot['db'] = db

    await set_default_commands(dp)
    await on_startup_notify(dp)

    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        # asyncio.run(main())
        asyncio.get_event_loop().run_until_complete(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
