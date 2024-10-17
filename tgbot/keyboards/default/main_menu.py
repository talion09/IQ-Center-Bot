from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📖 Предметы"),
            KeyboardButton(text="🎓 Преподаватели")
        ],
        [
            KeyboardButton(text="📝 Записаться")
        ],
        [
            KeyboardButton(text="ℹ️ О Нас"),
            KeyboardButton(text="☎️ Контакты"),
        ],
        [
            KeyboardButton(text="⚙️ Настройки")
        ],
        [
            KeyboardButton(text="Администрация"),
        ]
    ], resize_keyboard=True)


m_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📖 Предметы"),
            KeyboardButton(text="🎓 Преподаватели")
        ],
        [
            KeyboardButton(text="📝 Записаться")
        ],
        [
            KeyboardButton(text="ℹ️ О Нас"),
            KeyboardButton(text="☎️ Контакты"),
        ],
        [
            KeyboardButton(text="⚙️ Настройки")
        ],
        [
            KeyboardButton(text="💼 Личный Кабинет"),
        ]
    ], resize_keyboard=True)


admin_teacher_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📖 Предметы"),
            KeyboardButton(text="🎓 Преподаватели")
        ],
        [
            KeyboardButton(text="📝 Записаться")
        ],
        [
            KeyboardButton(text="ℹ️ О Нас"),
            KeyboardButton(text="☎️ Контакты"),
        ],
        [
            KeyboardButton(text="⚙️ Настройки")
        ],
        [
            KeyboardButton(text="Администрация"),
            KeyboardButton(text="💼 Личный Кабинет")
        ]
    ], resize_keyboard=True)



student_office = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="💳 Баланс"),
            KeyboardButton(text="⚖️ Оплатить")
        ],
        [
            KeyboardButton(text="🏡 Главное меню")
        ]
    ], resize_keyboard=True)


teacher_office = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="👥 Мои группы"),
            KeyboardButton(text="✉️ Мое описание")
        ],
        [
            KeyboardButton(text="🏡 Главное меню")
        ]
    ], resize_keyboard=True)