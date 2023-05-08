from aiogram.dispatcher import FSMContext
from aiogram import types

from states import Training
import markups as mks

from Database.database import add_imb
from IMB.index import count_index


async def get_height_weight(dp):

    @dp.callback_query_handler(lambda c: c.data == 'body_index', state='*')
    async def feeding_menu(callback_query: types.CallbackQuery):

        await callback_query.message.delete()

        await callback_query.message.answer("Введите свой рост")

        await Training.height.set()


    # Получение роста
    @dp.message_handler(state=Training.height)
    async def get_height(message: types.Message, state: FSMContext):

        if message.text == 'Отмена':

            await Training.default.set()

            await message.reply(message.from_user.id, 'Возвращаемся в меню!', reply_markup=mks.main_menu)

        else:

            user_height = message.text
            await state.update_data(height=user_height)

            await message.reply('Запомнил! Теперь введите Ваш вес.')

            await Training.weight.set()


    # Получение веса
    @dp.message_handler(state=Training.weight)
    async def get_weight(message: types.Message, state: FSMContext):

        if message.text == 'Назад':

            await Training.default.set()

            await message.reply(message.from_user.id, 'Возвращаемся в меню!', reply_markup=mks.main_menu)

        else:

            weight = message.text
            data = await state.get_data()
            height = data.get('height')

            try:

                index = count_index(height, weight)

            except:

                await state.finish()

            await Training.default.set()

            add_imb(message.from_user.id, index[0])

            await message.answer(index[1], parse_mode='HTML',reply_markup=mks.main_menu)