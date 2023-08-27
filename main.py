from aiogram import Dispatcher, Bot, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os

import Database.database as db
from Training import training
from IMB import feeding
import profile

from states import Training
import markups as mks
import config

bot = Bot(token=config.TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Функция инициализирующая БД
async def on_startup(_):
    await db.init_db()


# Хендлер, который срабатывает при вводе пользователем "/start"
@dp.message_handler(commands=['start'], state='*')
async def command_start(message: types.Message):

    '''# Удаление сообщения '/start' от пользователя
    try:
        await message.delete()
    except:
        pass
    '''

    # Сбор данных о пользователе
    user_id = message.from_user.id
    username = message.from_user.username

    # Вызов функции создания профиля (передачи данных в БД)
    await db.create_profile(user_id, username)

    # Сброс состояния
    await Training.default.set()

    # Приветственное сообщение
    welcomeText = (f'👋 Привет, <b>{message.from_user.first_name}</b>!\n'
                   f'🏋️ Я карманный <i>фитнес тренер</i>. '
                   f'С моей помощью ты сможешь:\n'
                   f'💪 Выбрать программу тренировок\n'
                   f'✍️ Составить рацион питания\n'
                   f'❤️ Следить за своим здоровьем')
    await bot.send_message(message.from_user.id, welcomeText, parse_mode = "HTML", reply_markup=mks.main_menu)


# Хендлер, который срабатывает при вводе пользователем "/admin"
@dp.message_handler(commands=['admin'], state = '*')
async def admin(message: types.Message):

    #Проверка на наличие прав администратора
    await db.check_admin(bot, dp, message.from_user.username, message.from_user.id)


# Хендлер, который срабатывает при нажатии пользователем кнопки, которая имеет callback "main_menu",
# далее по аналогии
@dp.callback_query_handler(lambda c: c.data == 'main_menu', state = '*')
async def main_menu(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    # Удаление предыдущего сообщения
    await callback_query.message.delete()

    # Стандартное состояние
    await Training.default.set()

    await callback_query.message.answer("🏠 Главное меню", reply_markup=mks.main_menu)


@dp.callback_query_handler(lambda c: c.data == 'trainings', state = '*')
async def trainings_menu(callback_query: types.CallbackQuery):

    await callback_query.message.delete()

    # Получение пути к файлу
    path = os.getcwd()
    # Вызов функции, инициализирующей тренировки
    await training.init_trainings(dp, path)
    await callback_query.message.answer("💪 Раздел с тренировками.\n"
                                        "👀 Я буду следить за твоими тренировками.\n️️"
                                        "✍️ Если у тебя еще нет программы, я помогу её составить!",
                                        reply_markup=mks.trainings_menu)


@dp.callback_query_handler(lambda c: c.data == 'feeding', state='*')
async def feeding_menu(callback_query: types.CallbackQuery):

    await callback_query.message.delete()

    await callback_query.message.answer("🍔 Здесь хранится твой рацион питания.\n"
                                        "✍️ Я готов составить тебе меню на день или неделю!",
                                        reply_markup=mks.feeding_menu)

    await feeding.get_height_weight(dp)


@dp.callback_query_handler(lambda c: c.data == 'profile', state='*')
async def profile_menu(callback_query: types.CallbackQuery):

    await callback_query.message.delete()

    await profile.profile(dp, callback_query)


if __name__ == '__main__':
    executor.start_polling(dp,
                           skip_updates=True,
                           on_startup=on_startup)
