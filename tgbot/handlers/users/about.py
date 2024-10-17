from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardRemove

from aiogram import Dispatcher
from aiogram import types

from tgbot.keyboards.inline.catalog import teacher_clb


# ℹ️ О Нас
async def about_bot(message: types.Message):
    await message.answer("Наш учебный центр - это современное образовательное учреждение, "
                         "которое стремится к качественной подготовке и развитию каждого студента.")


async def get_contacts(message: types.Message):
    await message.answer("Контактная информация: \n\n"
                         "Номер телефона: +998 90 014 64 32\n\n"
                         "Инстаграм\n"
                         "instagram.com/iqcenter.uz\n\n"
                         "Сайт iqcenter.uz")


def register_about(dp: Dispatcher):
    dp.register_message_handler(about_bot, text="ℹ️ О Нас")
    dp.register_message_handler(get_contacts, text="☎️ Контакты")













