from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from tgbot.handlers.users.start import bot_start
from tgbot.keyboards.default.phone import phonenumber
from tgbot.states.users import Custom


async def about_user(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    select = await db.select_user(telegram_id=int(message.from_user.id))
    name = select.get("full_name")
    phone = select.get("phone")
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    text1 = "Имя"
    text2 = "Номер телефона"
    text3 = "Назад"
    markup.insert(KeyboardButton(text=text1))
    markup.insert(KeyboardButton(text=text2))
    markup.insert(KeyboardButton(text=text3))
    await message.answer(f"{text1}: {name}\n{text2}: {phone}", reply_markup=markup)


async def name1(message: types.Message, state: FSMContext):
    cancel = ReplyKeyboardMarkup(resize_keyboard=True)
    cancel.add(KeyboardButton(text="Отменить"))
    text1 = "Введите Ваше Имя и Фамилию:"
    await message.answer(text1, reply_markup=cancel)
    await Custom.Name.set()


async def phone1(message: types.Message, state: FSMContext):
    text1 = "Отправьте ваш номер телефона (+998xxxxxxxxx):"
    number = ReplyKeyboardMarkup(resize_keyboard=True)
    number.add(KeyboardButton(text="📞 Поделиться контактом", request_contact=True))
    number.add(KeyboardButton(text="Отменить"))
    await message.answer(text1, reply_markup=number)
    await Custom.Phone.set()


# Custom.Name
async def name(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    text1 = "Отменить"
    text2 = "Изменение отменено"
    text3 = "Успешно изменено"
    text4 = "Введите Ваше Имя и Фамилию:"
    if message.text == text1:
        await state.reset_state()
        await message.answer(text2)
        await about_user(message, state)
    elif " " in str(message.text):
        await db.update_user(telegram_id=int(message.from_user.id), full_name=message.text)
        await state.reset_state()
        await message.answer(text3)
        await about_user(message, state)
    else:
        cancel = ReplyKeyboardMarkup(resize_keyboard=True)
        cancel.add(KeyboardButton(text="Отменить"))
        await message.answer(text4, reply_markup=cancel)
        await Custom.Name.set()


# Custom.Phone
async def phone(message: types.Message, state: FSMContext):
    db = message.bot.get("db")
    contc = message.contact.phone_number
    text3 = "Успешно изменено"
    await db.update_user(telegram_id=int(message.from_user.id), phone=int(contc))
    await state.reset_state()
    await message.answer(text3)
    await about_user(message, state)


# Custom.Phone
async def phone_text(message: types.Message, state: FSMContext):
    db = message.bot.get("db")

    text1 = "Отменить"
    text2 = "Изменение отменено"
    text3 = "Успешно изменено"
    text5 = "Отправьте ваш номер телефона (+998xxxxxxxxx):"

    if message.text == text1:
        await state.reset_state()
        await message.answer(text2)
        await about_user(message, state)
    else:
        number = ReplyKeyboardMarkup(resize_keyboard=True)
        number.add(KeyboardButton(text="📞 Поделиться контактом", request_contact=True))
        number.add(KeyboardButton(text="Отменить"))
        phone = message.text[1:]
        try:
            int(phone)
            if "+998" in str(message.text) and len(message.text) == 13:
                await db.update_user(telegram_id=int(message.from_user.id), phone=int(phone))
                await state.reset_state()
                await message.answer(text3)
                await about_user(message, state)
            else:
                await message.answer(text5, reply_markup=number)
                await Custom.Phone.set()
        except:
            await message.answer(text5, reply_markup=number)
            await Custom.Phone.set()


async def cancel1(message: types.Message, state: FSMContext):
    await bot_start(message, state)


def register_custom(dp: Dispatcher):
    dp.register_message_handler(about_user, text="⚙️ Настройки")
    dp.register_message_handler(name1, text="Имя")
    dp.register_message_handler(phone1, text="Номер телефона")
    dp.register_message_handler(cancel1, text="Назад")

    dp.register_message_handler(name, state=Custom.Name)
    dp.register_message_handler(phone_text, state=Custom.Phone, content_types=types.ContentType.TEXT)
    dp.register_message_handler(phone, state=Custom.Phone, content_types=types.ContentType.CONTACT)
