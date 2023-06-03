import markups as mks
from states import Admin
from aiogram import types
from aiogram.utils import exceptions
from openpyxl import Workbook
import asyncio

async def admin(bot, dp, user_id, db):

    await Admin.default.set() #передаем состояние админа (чтобы пользователи не имели доступа к этим хендлерам

    await bot.send_message(user_id, 'Вы админ', reply_markup=mks.admin_menu)

    cur = db.cursor() #создаем курсор для рассылки сообщений

    #рассылка сообщения всем пользователям
    @dp.callback_query_handler(lambda c: c.data and 'send_button' in c.data, state = Admin.default)
    async def process_callback_button1(callback_query: types.CallbackQuery):
        await bot.answer_callback_query(callback_query.id)

        await bot.send_message(user_id, 'Введите сообщение')

        await Admin.sending_message.set() #передаем состояние получения текста сообщения от пользователя

    @dp.message_handler(content_types=['text'], state = Admin.sending_message) #принимаем сообщение, действует только при состоянии Admin.sending_message
    async def get_text(message: types.Message):

        text = message.text #присваиваем текст сообщения от пользователя (администратора) в переменную, которую передадим как текст сообщения бота

        cur.execute('SELECT user_id FROM users') #выделяем всех пользователей из базы данных

        user = cur.fetchall() #помещаем всех пользователей из бд в переменную

        for row in user: #для каждого ряда из списка пользователей

            #создаем исключение с рядом возможных ошибок
            try:
                await bot.send_message(row[0], text)
            except exceptions.BotBlocked:
                print(f"Пользователь {user} заблокировал этого бота")
            except exceptions.ChatNotFound:
                print(f"Чат пользователя {user} не найден")
            except exceptions.RetryAfter as e:
                print(f"Апи отправило слишком много запросов, нужно немного подождать {e.timeout} секунд")
                await asyncio.sleep(e.timeout)
            except exceptions.TelegramAPIError:
                print(f"Ошибка Telegram API для пользователя {user}")

        await Admin.default.set() #возвращаем обычное состояние админа, чтобы сообщения не дублировались всем пользователям
        await bot.send_message(message.from_user.id, 'Сообщение отправлено всем пользователям', reply_markup=mks.to_menu_markup)

    #выгрузка базы данных
    @dp.callback_query_handler(lambda c: c.data and 'download' in c.data, state = Admin.default)
    async def process_callback_button1(callback_query: types.CallbackQuery):

        await bot.answer_callback_query(callback_query.id)

        cur.execute('SELECT * FROM users')  # выбираем всю таблицу users
        data = cur.fetchall()  # передаем

        wb = Workbook()  # создаем воркбук для конвертирования бд
        ws = wb.active

        for row in data:
            ws.append(row)

        wb.save('users.xlsx')

        with open('users.xlsx', "rb") as file:
            await bot.send_document(callback_query.from_user.id, file, reply_markup=mks.admin_menu)

    #возврат в меню админа
    @dp.callback_query_handler(lambda c: c.data and 'admin' in c.data, state = Admin.default)
    async def process_callback_button1(callback_query: types.CallbackQuery):

        await bot.send_message(user_id, 'Меню администратора', reply_markup=mks.admin_menu)