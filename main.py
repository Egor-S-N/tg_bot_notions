from aiogram import Bot, Dispatcher, executor, types
import db
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup,ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils import callback_data
import datetime 
from datetime import date
BOT_TOKEN = '6316810112:AAHoKOAlvGQHowIHp5p_s3jASdHuO2JVRI0'
ADMIN_USERNAME = 'niktoservitor'
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


NOTE_TITLE = ""
NOTE_BODY = ""
NOTE_PASSWORD = ""
notion_id = 0
notes_count = 0
filter = "year"
filter_value = "01"
notes = []


# Создаем CallbackData для обработки нажатий на кнопки
switch_notes_callback = callback_data.CallbackData("switch_notes", "page")
# Определение состояний для FSM


class AdminCommands(StatesGroup):
    waiting_for_title = State()
    waiting_for_body = State()
    waiting_for_code = State()
# Определение состояний для FSM


class UserStates(StatesGroup):
    waiting_for_code = State()
    waiting_for_confirm = State()
    waitng_for_comment = State()
    waiting_for_reaction = State()
    waiting_for_email = State()
# Определение состояний для FSM


class MenuStates(StatesGroup):
    main_menu = State()
# Обработчик команды /start


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    if message.from_user.username == ADMIN_USERNAME:
        await message.reply(f"Приветствую, {message.from_user.first_name}. \nВы - администратор данного бота", reply_markup=get_admin_keybord())
    else:
        if not db.check_user(message.from_user.id):
            db.create_user(message.from_user.id)
        if not db.get_status(message.from_user.id):
            await UserStates.waiting_for_confirm.set()
            await message.reply("Здравствуйте, рады видеть вас.\nДля начала, пожалуйста, ознакомтесь с пользователским соглашением https://teletype.in/ , а затем примите пользовательские соглашения по кнопке ниже", reply_markup=get_acceptance_keyboard())
        else:
            await message.reply("Здравствуйте, рады видеть вас снова. Какую категорию материалов вы хотите просмотреть?",
                                reply_markup=get_user_keybord())



@dp.message_handler(text=['Показать категории заметок',
                          'Как поддержать проект', 'Показать мои комментарии'])
async def menu_button_handler(message: types.Message):
    choose = message.text

    if choose == 'Показать категории заметок':
        await bot.send_message(message.from_user.id, "Выберите категорию материалов", reply_markup=get_notes_keyboard())
    elif choose == 'Как поддержать проект':
        support_account = "@niktoservitor"
        await bot.send_message(message.from_user.id, f"Поддержать проект можно через данный аккаунт: {support_account}", reply_markup=get_user_keybord())
    elif choose == 'Показать мои комментарии':
        my_comments = db.get_person_comments(message.from_user.id)
        total_pages = (len(db.get_person_comments(
            message.chat.id)) - 1) // 10 + 1
        await bot.send_message(message.from_user.id, f"Вот список ваших коментариев:", reply_markup=create_comments_keyboard(my_comments, 1, total_pages))

#клавиатура личных  комментариев пользователя
def get_my_comments_keyboard(comments, current_page, total_pages):
    keyboard = types.InlineKeyboardMarkup(row_width=1)

    start_index = (current_page - 1) * 10
    end_index = start_index + 10

    # Отображение комментариев на текущей странице
    for comment in comments[start_index:end_index]:
        comment_button = types.InlineKeyboardButton(
            f"{comment[2]}", callback_data=f"comment_{comment[0]}")
        keyboard.add(comment_button)
    if len(comments) > 10:
        # Добавление кнопок переключения страницdb.get_comments()
        if total_pages > 1:
            if current_page > 1:
                prev_page_button = types.InlineKeyboardButton(
                    "<< Назад", callback_data=f"prev_mc_page_{current_page}")
                keyboard.add(prev_page_button)

            if current_page < total_pages:
                next_page_button = types.InlineKeyboardButton(
                    "Вперед >>", callback_data=f"next_mc_page_{current_page}")
                keyboard.add(next_page_button)

    return keyboard


# Обработчик событий callback_query для переключения страницы личных комментариев пользователя  
@dp.callback_query_handler(lambda query: query.data.startswith(('prev_mc_page_', 'next_mc_page_')))
async def switch_comments_page_handler(query: types.CallbackQuery):
    current_page = int(query.data.split('_')[3])
    total_pages = (len(db.get_person_comments(
        query.message.chat.id)) - 1) // 10 + 1
    # Обработка нажатия кнопки "Назад"
    if query.data.startswith('prev_mc_page_'):
        current_page -= 1
    # Обработка нажатия кнопки "Вперед"
    elif query.data.startswith('next_mc_page_'):
        current_page += 1

    # Создание инлайн-клавиатуры для списка комментариев
    keyboard = get_my_comments_keyboard(db.get_person_comments(
        query.message.chat.id), current_page, total_pages)

    # Обновление сообщения с инлайн-клавиатурой
    await bot.edit_message_reply_markup(chat_id=query.message.chat.id, message_id=query.message.message_id, reply_markup=keyboard)


# клавиатура для принятия пользовательских соглашений
def get_acceptance_keyboard():
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True)
    accept_button = KeyboardButton('Принять соглашения')
    keyboard.add(accept_button)
    return keyboard



# Создание инлайн-клавиатуры для списка комментариев с учетом текущей страницы
def create_comments_keyboard(comments, current_page, total_pages):
    # Создание инлайн-клавиатуры
    keyboard = types.InlineKeyboardMarkup(row_width=1)

    # Вычисление начального и конечного индексов комментариев на текущей странице
    start_index = (current_page - 1) * 10
    end_index = start_index + 10

    # Отображение комментариев на текущей странице
    for comment in comments[start_index:end_index]:
        comment_button = types.InlineKeyboardButton(
            f"{comment[2]}", callback_data=f"comment_{comment[0]}")
        keyboard.add(comment_button)
    if len(comments) > 10:
        # Добавление кнопок переключения страниц
        if total_pages > 1:
            if current_page > 1:
                prev_page_button = types.InlineKeyboardButton(
                    "<< Назад", callback_data=f"prev_page_{current_page}")
                keyboard.add(prev_page_button)

            if current_page < total_pages:
                next_page_button = types.InlineKeyboardButton(
                    "Вперед >>", callback_data=f"next_page_{current_page}")
                keyboard.add(next_page_button)

    return keyboard

# Обработчик событий callback_query для переключения страницы комментариев


@dp.callback_query_handler(lambda query: query.data.startswith(('prev_page_', 'next_page_')))
async def switch_comments_page_handler(query: types.CallbackQuery):
    current_page = int(query.data.split('_')[2])
    total_pages = (len(db.get_comments()) - 1) // 10 + 1
    # Обработка нажатия кнопки "Назад"
    if query.data.startswith('prev_page_'):
        current_page -= 1
    # Обработка нажатия кнопки "Вперед"
    elif query.data.startswith('next_page_'):
        current_page += 1

    # Создание инлайн-клавиатуры для списка комментариев
    keyboard = create_comments_keyboard(
        db.get_comments(), current_page, total_pages)

    # Обновление сообщения с инлайн-клавиатурой
    await bot.edit_message_reply_markup(chat_id=query.message.chat.id, message_id=query.message.message_id, reply_markup=keyboard)

# Обработчик событий callback_query для просмотра деталей комментария
@dp.callback_query_handler(lambda query: query.data.startswith('comment_'))
async def comment_details_handler(query: types.CallbackQuery):
    comment_id = int(query.data.split('_')[1])

    # Поиск комментария по его идентификатору
    comment = next((c for c in db.get_comments() if c[0] == comment_id), None)

    if comment:
        # Отправка сообщения с деталями комментария
        await bot.send_message(query.message.chat.id, f"Комментарий к заметке {comment[1]}")
        await bot.send_message(query.message.chat.id, f"{comment[2]}")
    else:
        await bot.send_message(query.message.chat.id, "Комментарий не найден")

#основная клавиатура администратора
def get_admin_keybord():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    add_new_note_btn = KeyboardButton(text="Добавить новую заметку")
    show_comments_btn = KeyboardButton(text="Показать комментарии")
    show_reactions_btn = KeyboardButton(text="Показать реакции")
    keyboard.add( add_new_note_btn,
                 show_comments_btn, show_reactions_btn)
    return keyboard

# Создание инлайн-клавиатуры для списка комментариев с учетом текущей страницы
def create_reactions_keyboard(reactions, current_page, total_pages):
    # Создание инлайн-клавиатуры
    keyboard = types.InlineKeyboardMarkup(row_width=1)

    # Вычисление начального и конечного индексов комментариев на текущей странице
    start_index = (current_page - 1) * 10
    end_index = start_index + 10

    # Отображение комментариев на текущей странице
    for reaction in reactions[start_index:end_index]:
        comment_button = types.InlineKeyboardButton(
            f"{reaction[2]}", callback_data=f"react_{reaction[0]}")
        keyboard.add(comment_button)
        # Добавление кнопок переключения страниц
    if total_pages > 1:
        if current_page > 1:
            prev_page_button = types.InlineKeyboardButton(
                "<< Назад", callback_data=f"prev_page_react_{current_page}")
            keyboard.add(prev_page_button)

        if current_page < total_pages:
            next_page_button = types.InlineKeyboardButton(
                "Вперед >>", callback_data=f"next_page_react_{current_page}")
            keyboard.add(next_page_button)

    return keyboard

@dp.callback_query_handler(lambda query: query.data.startswith('prev_page_react_'))
async def prev_page_react_handler(query: types.CallbackQuery):
    # current_page = 1  # Получите текущую страницу из контекста или другого источника
    current_page = int(query.data.split('_')[3])
    total_pages = (len(db.get_reactions()) - 1) // 10 + 1
    # Обработка нажатия кнопки "Назад"
    # if query.data == 'prev_page_react':
    current_page -= 1
    # Создание инлайн-клавиатуры для списка комментариев
    keyboard = create_reactions_keyboard(
        db.get_reactions(), current_page, total_pages)

    # Обновление сообщения с инлайн-клавиатурой
    await bot.edit_message_reply_markup(chat_id=query.message.chat.id, message_id=query.message.message_id, reply_markup=keyboard)

@dp.callback_query_handler(lambda query: query.data.startswith('next_page_react_'))
async def next_page_react_handler(query: types.CallbackQuery):
    current_page = 1  # Получите текущую страницу из контекста или другого источника
    total_pages = (len(db.get_reactions()) - 1) // 10 + 1
    # Обработка нажатия кнопки "Назад"
    current_page += 1
    # Создание инлайн-клавиатуры для списка комментариев
    keyboard = create_reactions_keyboard(
        db.get_reactions(), current_page, total_pages)

    # Обновление сообщения с инлайн-клавиатурой
    await bot.edit_message_reply_markup(chat_id=query.message.chat.id, message_id=query.message.message_id, reply_markup=keyboard)


# Обработчик событий callback_query для просмотра деталей комментария
@dp.callback_query_handler(lambda query: query.data.startswith('comment_'))
async def comment_details_handler(query: types.CallbackQuery):
    comment_id = int(query.data.split('_')[1])

    # Поиск комментария по его идентификатору
    comment = next((c for c in db.get_comments() if c[0] == comment_id), None)

    if comment:
        # Отправка сообщения с деталями комментария
        await bot.send_message(query.message.chat.id, f"Комментарий к заметке {comment[1]}")
        await bot.send_message(query.message.chat.id, f"{comment[2]}")
    else:
        await bot.send_message(query.message.chat.id, "Комментарий не найден")

#основная клавиатура пользователя 
def get_user_keybord():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    get_notes_btn = KeyboardButton(text="Показать категории заметок")
    help_btn = KeyboardButton(text="Как поддержать проект")
    my_comments_btn = KeyboardButton(text="Показать мои комментарии")

    keyboard.add(get_notes_btn, help_btn, my_comments_btn)
    return keyboard

#клавиатура для выбора категорий заметок 
def get_notes_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    daily_notes_button = KeyboardButton('Заметки по ежедневным видео')
    weekly_notes_button = KeyboardButton('Заметки по еженедельным видео')
    monthly_notes_button = KeyboardButton('Заметки по ежемесячным видео')
    back_to_menu_button = KeyboardButton('Вернуться назад в меню')
    archive_button = KeyboardButton('Архивы')
    keyboard.add(daily_notes_button, weekly_notes_button,
                 monthly_notes_button, archive_button, back_to_menu_button)
    return keyboard

#клавиатура выбора заметок по месяцам 
def get_month_notes_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().month
    for month in range(1, current_month + 1):
        month_button = KeyboardButton(f'Заметки за {month}.{current_year}')
        keyboard.add(month_button)
    keyboard.add(KeyboardButton('Назад'))
    return keyboard



# Обработчик нажатия кнопки принятия соглашений
@dp.message_handler(text='Принять соглашения', state=UserStates.waiting_for_confirm)
async def accept_button_handler(message: types.Message, state: FSMContext):
    await bot.send_message(message.chat.id, 'Вы приняли пользовательские соглашения',
                           reply_markup=None, disable_notification=True)
    await state.finish()
    db.edit_user_confirm(message.from_user.id)
    
    await bot.send_message(message.from_user.id,  "Спасибо, теперь вам доступны новые возможности", reply_markup=get_user_keybord())
    # await UserStates.waiting_for_email.set()

#обработчик перехода в главное меню
@dp.message_handler(text='Вернуться назад в меню')
async def go_back_click(message: types.Message):
    await bot.send_message(message.chat.id, "Переход в главное меню", reply_markup=get_user_keybord())

#вывод ежедневвных заметок 
@dp.message_handler(text='Заметки по ежедневным видео')
async def daily_notes_handler(message: types.Message):
    day = datetime.datetime.now().date()

    values = db.get_notes("day", str(day))
    if len(values) == 0:
        await bot.send_message(message.chat.id, 'Пока что заметок на сегодня нету')
    else:
        global filter, filter_value, notes_count
        filter = 'day'
        filter_value = day
        notes_count = len(values)
        await bot.send_message(message.chat.id, f'Вы выбрали заметки по ежедневным видео.\nТекущая дата: {day}.\nВот список заметок', reply_markup=create_notes_keyboard(notes_count, 1))

#вывод еженедельных заметок 
@dp.message_handler(text='Заметки по еженедельным видео')
async def weekly_notes_handler(message: types.Message):
    # Получение текущей даты
    today = datetime.date.today()

    # Определение первого дня текущей недели (понедельник)
    start_of_week = today - datetime.timedelta(days=today.weekday())

    # Определение всех дат в текущей неделе
    dates_in_week = [start_of_week +
                     datetime.timedelta(days=i) for i in range(7)]

    global notes_count, notes
    notes = []
    for i in dates_in_week:
        values = db.get_notes("day", i)
        if values != []:
            for j in values:
                notes.append(j)
    notes_count = len(notes)
    
    await bot.send_message(message.chat.id, f'Вы выбрали категорию: Заметки по еженедельным видео', reply_markup=create__week_notes_keyboard(notes_count, 1, notes))


#генерация списка ежедневных заметок 
def create__week_notes_keyboard(total_notes, current_page, values):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    notes_per_page = 5
    # Вычисляем количество страниц
    total_pages = (total_notes - 1) // notes_per_page + 1

    # Вычисляем начальный и конечный индексы заметок на текущей странице
    start_index = (current_page - 1) * notes_per_page
    end_index = min(start_index + notes_per_page, total_notes)

    # Создаем кнопки для каждой заметки на текущей странице
    for i in range(start_index, end_index):
        note_button = types.InlineKeyboardButton(
            f"{values[i][1]}", callback_data=f"view_note_{values[i][0]}")
        keyboard.add(note_button)

    # Добавляем кнопки переключения страниц
    if total_pages > 1:
        if current_page > 1:
            prev_page_button = types.InlineKeyboardButton(
                "<< Назад", callback_data=f"switch_week_page_{current_page-1}")
            keyboard.insert(prev_page_button)

        if current_page < total_pages:
            next_page_button = types.InlineKeyboardButton(
                "Вперед >>", callback_data=f"switch_week_page_{current_page+1}")
            keyboard.insert(next_page_button)

    return keyboard

# Обработчик перелистывания страниц по еженедельным 
@dp.callback_query_handler(lambda query: query.data.startswith('switch_week_page_'))
async def switch_page_callback_handler(query: types.CallbackQuery):
    page_number = int(query.data.split('_')[3])
    await query.answer()
    await bot.edit_message_reply_markup(chat_id=query.message.chat.id, message_id=query.message.message_id,
                                        reply_markup=create__week_notes_keyboard(total_notes=notes_count, current_page=page_number, values=notes))


#Вывод списка по месяцам 
@dp.message_handler(text='Заметки по ежемесячным видео')
async def monthly_notes_handler(message: types.Message):
    await bot.send_message(message.chat.id, 'Выберите месяц:', reply_markup=get_month_notes_keyboard())

#Вывод списка годов 
@dp.message_handler(text='Архивы')
async def archive_handler(message: types.Message):
    await bot.send_message(message.chat.id, 'Выберите год:', reply_markup=get_archive_keyboard())

#все заметки за выбранный месяц 
@dp.message_handler(lambda message: message.text.startswith('Заметки за '))
async def month_notes_handler(message: types.Message):
    month_year = message.text.split(' ')[-1]
    month = '0'+month_year.split('.')[0]

    values = db.get_notes('month', month)
    global filter, filter_value, notes_count
    filter = 'month'
    filter_value = month
    notes_count = len(values)
    months = {
        '01': 'январь',
        '02': 'февраль',
        '03': 'март',
        '04': 'апрель',
        '05': 'май',
        '06': 'июнь',
        '07': 'июль',
        '08': 'август',
        '09': 'сентябрь',
        '10': 'октябрь',
        '11': 'ноябрь',
        '12': 'декабрь'
    }
    if notes_count == 0:
        await bot.send_message(message.chat.id, "В выбранный вами месяц небыло заметок", reply_markup=get_notes_keyboard())
    else:
        await bot.send_message(message.chat.id, f'Вы выбрали заметки за {months[month]}', reply_markup=create_notes_keyboard(notes_count, 1))

#Переход назад
@dp.message_handler(text='Назад')
async def back_handler(message: types.Message):
    await bot.send_message(message.chat.id, 'Возврат в главное меню', reply_markup=get_user_keybord())

#Клавиатура для выбора года 
def get_archive_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for year in db.get_years():
        year_button = KeyboardButton(str(year))
        keyboard.add(year_button)

    keyboard.add(KeyboardButton('Назад'))
    return keyboard

# Создание Inline клавиатуры выбора вкладок
def create_tabs_keyboard(tabs):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for tab in range(tabs):
        tab_button = types.InlineKeyboardButton(
            tab, callback_data=f"select_tab_{tab}")
        keyboard.add(tab_button)
    return keyboard

# Создаем Inline клавиатуру с кнопками переключения заметок
def create_notes_keyboard(total_notes, current_page):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    notes_per_page = 5
    # Вычисляем количество страниц
    total_pages = (total_notes - 1) // notes_per_page + 1

    # Вычисляем начальный и конечный индексы заметок на текущей странице
    start_index = (current_page - 1) * notes_per_page
    end_index = min(start_index + notes_per_page, total_notes)

    # Создаем кнопки для каждой заметки на текущей странице
    for i in range(start_index, end_index):
        note_button = types.InlineKeyboardButton(
            f"{db.get_notes(filter, filter_value)[i][1]}", callback_data=f"view_note_{db.get_notes(filter, filter_value)[i][0]}")
        keyboard.add(note_button)

    # Добавляем кнопки переключения страниц
    if total_pages > 1:
        if current_page > 1:
            prev_page_button = types.InlineKeyboardButton(
                "<< Назад", callback_data=f"switch_page_{current_page-1}")
            keyboard.insert(prev_page_button)

        if current_page < total_pages:
            next_page_button = types.InlineKeyboardButton(
                "Вперед >>", callback_data=f"switch_page_{current_page+1}")
            keyboard.insert(next_page_button)

    return keyboard

# Обработчик перелистывания страниц заметок 
@dp.callback_query_handler(lambda query: query.data.startswith('switch_page_'))
async def switch_page_callback_handler(query: types.CallbackQuery):
    page_number = int(query.data.split('_')[2])
    await query.answer()
    await bot.edit_message_reply_markup(chat_id=query.message.chat.id, message_id=query.message.message_id,
                                        reply_markup=create_notes_keyboard(total_notes=notes_count, current_page=page_number))

#Обработчик возврата в меню 
@dp.callback_query_handler(lambda query: query.data.startswith('go_to_menu'))
async def go_to_menu(query: types.CallbackQuery):
    await bot.send_message(query.message.chat.id, "Возврат в главное меню", reply_markup=get_user_keybord())

#Ввод пароля для заметки 
@dp.message_handler(state=UserStates.waiting_for_code)
async def user_input_handler(message: types.Message, state: FSMContext):
    note = db.get_one_note(notion_id)
    if message.text == "Назад":
        await bot.send_message(message.chat.id, text="Возврат в главное меню.\nВыберите действие:", reply_markup=get_user_keybord())
        await state.finish()

    elif message.text == note[4] :
        await bot.send_message(message.chat.id, f"<i>{note[1]}</i> \n\n {note[2]} \n\n Дата создания: {note[3]}", reply_markup=get_callback_keybord(), parse_mode=types.ParseMode.HTML)
        await state.finish()

    else:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        back_btn = KeyboardButton('Назад')
        keyboard.add(back_btn)
        await message.reply("Вы ввели неверный код. Проверьте корректность вашего пароля", reply_markup=keyboard)

#Нажатие кнопки для ввода пароля от заметки 
@dp.callback_query_handler(lambda query: query.data.startswith('view_note_'))
async def view_note_callback_handler(query: types.CallbackQuery):

    note_number = int(query.data.split('_')[2])
    global notion_id
    notion_id = note_number
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    back_btn = KeyboardButton('Назад')
    keyboard.add(back_btn)
    await bot.send_message(query.message.chat.id, "Пожалуйста введите кодовое слово для доступа к данной замете:", reply_markup=keyboard)
    await UserStates.waiting_for_code.set()

# Клавиатура выбора комментария или реакции
def get_callback_keybord():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    comment_button = KeyboardButton('Добавить комментарий')
    reaction_button = KeyboardButton('Добавить реакцию')
    back_button = KeyboardButton('Назад')
    keyboard.add(comment_button, reaction_button, back_button)
    return keyboard

# Обработчик выбора комментария или реакции
@dp.message_handler(text=['Добавить реакцию', 'Добавить комментарий'])
async def callback_button_handler(message: types.Message):
    if message.text == 'Добавить реакцию':
        await bot.send_message(message.chat.id, 'Вот список доступных реакций', reply_markup=ReplyKeyboardRemove(), disable_notification=True)
        await bot.send_message(message.chat.id, 'Ниже укажите вашу реакцию', reply_markup=reactions_keyboard(), disable_notification=True)
        await UserStates.waiting_for_reaction.set()
    elif message.text == 'Добавить комментарий':
        await bot.send_message(message.chat.id, 'Ниже укажите ваш комментарий', reply_markup=ReplyKeyboardRemove(), disable_notification=True)
        await UserStates.waitng_for_comment.set()


# Добавление комментария
@dp.message_handler(state=UserStates.waitng_for_comment.state)
async def waiting_callback_handler(message: types.Message, state: FSMContext):
    db.add_comment(notion_id, message.text, message.chat.id)
    await bot.send_message(message.chat.id, "Комментарий успешно добавлен", reply_markup=get_notes_keyboard())
    await state.finish()

# Выбор архивов по годам
@dp.message_handler(lambda message: message.text.isnumeric())
async def year_archive_handler(message: types.Message):
    year = int(message.text)
    await bot.send_message(message.chat.id, f'Вы выбрали архив за {year} год.', reply_markup=ReplyKeyboardRemove())
    global filter
    filter = "year"
    global filter_value
    filter_value = str(year)
    notes_count = db.get_notes_count(filter, filter_value)
    await bot.send_message(message.chat.id, 'вот список всех заметок: ', reply_markup=create_notes_keyboard(notes_count, 1))

# Создание инлайн-клавиатуры с кнопками реакций
def reactions_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=3)
    reaction1_button = InlineKeyboardButton("😀", callback_data='reaction_1')
    reaction2_button = InlineKeyboardButton("😆", callback_data='reaction_2')
    reaction3_button = InlineKeyboardButton("😊", callback_data='reaction_3')
    reaction4_button = InlineKeyboardButton("❤️", callback_data='reaction_4')
    reaction5_button = InlineKeyboardButton("💪", callback_data='reaction_5')
    reaction6_button = InlineKeyboardButton("😳", callback_data='reaction_6')
    reaction7_button = InlineKeyboardButton("😫", callback_data='reaction_7')
    reaction8_button = InlineKeyboardButton("😭", callback_data='reaction_8')
    reaction9_button = InlineKeyboardButton("😰", callback_data='reaction_9')
    keyboard.add(reaction1_button, reaction2_button, reaction3_button)
    keyboard.add(reaction4_button, reaction5_button, reaction6_button)
    keyboard.add(reaction7_button, reaction8_button, reaction9_button)
    return keyboard

# Обработчик событий выбора реакции
@dp.callback_query_handler(lambda query: query.data.startswith('reaction_'), state=UserStates.waiting_for_reaction.state)
async def pick_reaction(query: types.CallbackQuery, state: FSMContext):
    reactions = {1: '😀', 2: '😆', 3: '😊', 4: '❤️',
                 5: '💪', 6: '😳', 7: '😫', 8: '😭', 9: '😰'}
    value = int(query.data.split('_')[1])
    req = reactions[value]
    await state.finish()
    db.add_reaction(notion_id, reactions[value])
    await bot.edit_message_reply_markup(chat_id=query.message.chat.id, message_id=query.message.message_id, reply_markup=None)
    await bot.send_message(query.message.chat.id, "Ваша реакция успешно добавлена", reply_markup=get_notes_keyboard())




#----------------------------------------------------------------возможности администратора
# обработчик кнопки администратора "показать комментарии"
@dp.message_handler(text="Показать комментарии")
async def show_comments_handler(message: types.Message):
    if message.from_user.username == ADMIN_USERNAME:
        comments_per_page = 10
    # Получение параметров текущей страницы и общего количества страниц
        current_page = 1
        comments = db.get_comments()
        total_pages = (len(comments) - 1) // comments_per_page + 1
        
        # Создание инлайн-клавиатуры для списка комментариев
        keyboard = create_comments_keyboard(
            comments, current_page, total_pages)

        # Отправка сообщения с инлайн-клавиатурой
        if len(comments) != 0:
            await bot.send_message(message.from_user.id, "Список комментариев:", reply_markup=keyboard)
        else:
            await bot.send_message(message.from_user.id, "Список комментариев пуст")


#Обработчик кнопки добавления новой заметки 
@dp.message_handler(text = "Добавить новую заметку")
async def add_new_note_click(message: types.Message):
    if message.from_user.username == ADMIN_USERNAME:
        await bot.send_message(message.from_user.id,text="Пожалуйста, укажите заголовок заметки: ", reply_markup=ReplyKeyboardRemove())
        await AdminCommands.waiting_for_title.set()
    else:
        await bot.send_message(message.from_user.id,text = "Вы не являитесь администратором")

#Ожидание добавления заголовка
@dp.message_handler(state=AdminCommands.waiting_for_title)
async def process_title(message: types.Message, state: FSMContext):
    # Получаем текст заголовка
    title = message.text.strip()
    if title  == "":
        return
    global NOTE_TITLE
    NOTE_TITLE = title
    await message.reply(f"Заголовок заметки сохранен.\nВведите тело заметки:", reply_markup=ReplyKeyboardRemove())
    await AdminCommands.waiting_for_body.set()

#ожидание добавления тела 
@dp.message_handler(state=AdminCommands.waiting_for_body)
async def process_body(message: types.Message, state: FSMContext):
    # Получаем текст тела заметки
    body = message.text.strip()
    if body == "":
        return 
    global NOTE_BODY
    NOTE_BODY = body

    # db.add_note(NOTE_TITLE, NOTE_BODY)
    await message.reply(f"Тело заметки сохранено.\nВведите пароль для заметки:", reply_markup=ReplyKeyboardRemove())
    await AdminCommands.waiting_for_code.set()

#Ожидание добавления пароля 
@dp.message_handler(state=AdminCommands.waiting_for_code)
async def process_password(message: types.Message, state: FSMContext):
    # Получаем текст тела заметки
    password = message.text.strip()
    if password == "":
        return 
    global NOTE_PASSWORD
    NOTE_PASSWORD = password

    db.add_note(NOTE_TITLE, NOTE_BODY, NOTE_PASSWORD)
    current_date = date.today()
    for user in db.get_users_id():
        await bot.send_message(user[0], f"Была добавлена новая заметка!!\nНе пропустите.\nТема заметки: {NOTE_TITLE}\nДата заметки: {current_date   } ")
    await message.reply(f"Пароль заметки сохранен.\nПроцесс создания заметки завершен.", reply_markup=get_admin_keybord())
    await state.finish()

# обработчик кнопки администратора "показать реакции"
@dp.message_handler(text="Показать реакции")
async def show_reactions_handler(message: types.Message):
    if message.from_user.username == ADMIN_USERNAME:
        comments_per_page = 10
    # Получение параметров текущей страницы и общего количества страниц
        current_page = 1
        reactions = db.get_reactions()
        total_pages = (len(reactions) - 1) // comments_per_page + 1


        # Создание инлайн-клавиатуры для списка комментариев
        keyboard = create_reactions_keyboard(
            reactions, current_page, total_pages)
        if len(reactions) != 0:
        # Отправка сообщения с инлайн-клавиатурой
            await bot.send_message(message.from_user.id, "Список реакций:", reply_markup=keyboard)
        else:
            await bot.send_message(message.from_user.id, "Список реакций пуст")


# Запуск бота
if __name__ == '__main__':
    db.create_tables()
    executor.start_polling(dp, skip_updates=True)
