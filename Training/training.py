from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from Database import database as db
from states import Training
import markups as mks
from time import sleep
import os

async def init_trainings(dp, path):

    # Создание стандартных категорий тренировок в виде папок
    try:
        os.mkdir(f'{path}\Training\Trainings\Набор веса')
        os.mkdir(f'{path}\Training\Trainings\Похудение')
        os.mkdir(f'{path}\Training\Trainings\Удержание веса')

    except:
        pass


    # Функция начала тренировок
    async def start_training(training_info, callback_query, state):

        # Состояние активной тренировки
        await Training.active_training.set()

        try:
            # Открытие файла тренировки через путь, который берется из БД
            with open(f'{path}/Training/Trainings/{training_info[0]}/{training_info[1]}/{training_info[2]}.txt', encoding="utf-8") as file:
                lines = file.readlines()

                # Сохранение данных о тренировке в хранилище
                await state.update_data(lines = lines, line_number = 0)

            await callback_query.message.answer('Вы готовы начать тренировку?',
                                                reply_markup=mks.start_training_menu)
        # Если такого пути не существует, значит пользователь не выбрал тренировку/тренировка была удалена(и т.п.)
        except FileNotFoundError:

            await callback_query.message.answer('Вы еще не выбрали тренировку!',
                                                reply_markup=mks.not_chosen_training)

    # Хендлер, срабатывающий при нажатии на кнопку '🟢 Начать' и '🛑 Отмена'
    @dp.callback_query_handler(lambda c: c.data == 'next_exercise', state = Training.active_training)
    async def next_exercise(callback_query: CallbackQuery, state: FSMContext):

        await callback_query.message.delete()

        # Получение данных из хранилища
        data = await state.get_data()
        lines = data['lines']
        line_number = data['line_number']

        try:

            # Разделение строки по ":"
            line = lines[line_number].split(':')

            '''
            line[0] - Название упражнения
            line[1] - Количество подходов
            line[2] - Ссылка на видео
            line[3 - ... (нечетные)] - Кол-во повторений
            line[4 - ... (четные)] - Секунды отдыха
            '''

            exercise_message = await callback_query.message.answer(
                f'Упражнение: <b>{line[0]}</b>\nКоличество подходов: <b>{line[1]}</b>\n\nВидео: <i>{line[2]}</i>',
                parse_mode='HTML',
                reply_markup=mks.active_training_menu)

        # Когда строки в файле заканчиваются, вызывается исключение об окончании тренировки
        except IndexError:

            await callback_query.message.answer('🎉 Поздравляю, тренировка закончена!', reply_markup=mks.to_menu_only)

            # Получение конкретной тренировки из БД (путь, категория, тренировка, день)
            current_training_info = db.get_training(callback_query.from_user.id)
            trainings_list = os.listdir(f'{path}\Training\Trainings\\{current_training_info[0]}\\{current_training_info[1]}')
            day = int(current_training_info[2]) # day получает название файла тренировки

            if day < len(trainings_list):

                new_day = day + 1

            else:

                new_day = 1

            # Передача тренировки в БД
            db.set_training(callback_query.from_user.id, current_training_info[0], current_training_info[1], new_day)

            # Обновление количества завершенных тренировок
            db.update_trainings_count(callback_query.from_user.id)

        # Т.к. строки могут закончиться, необходимо вызвать исключение
        try:

            await state.update_data(iteration=3, line=line, exercise_message=exercise_message)

        except:

            pass


    # Хендлер, срабатывающий при нажатии на кнопку "➡ Далее"
    @dp.callback_query_handler(lambda c: c.data == 'next_iteration', state = Training.active_training)
    async def continue_training(callback_query: CallbackQuery, state: FSMContext):

        # Получение данных из хранилища
        data = await state.get_data()
        iteration = data['iteration']
        line = data['line']
        exercise_message = data['exercise_message']

        # Проверка на существование данных подхода. Через исключение, т.к. могут закончиться
        try:

            iteration_message = data['iteration_message']
            await iteration_message.delete()

        except:

            pass

        # Если позиция числа из файла нечетная и меньше длины файла, значит это кол-во повторений
        if iteration % 2 and iteration < len(line):

            iteration_message = await callback_query.message.answer(f'Количество повторений: {line[iteration]}')
            await state.update_data(iteration_message = iteration_message)

        # Если позиция числа из файла четная и меньше длины файла, значит это кол-во секунд отдыха
        elif iteration % 2 == 0 and iteration < len(line):

            iteration_message = await callback_query.message.answer(f'⏳ Отдых - {line[iteration]} сек.', reply_markup=mks.active_training_skip_timer_menu)
            await exercise_message.edit_reply_markup(None)
            # Цикл на отдых (от кол-ва секунд отдыха до нуля)
            for seconds in range(int(line[iteration])-1, 0, -1):

                # Если значение проверки = 0 (по умолчанию), то таймер продолжает работать
                if db.check_timer(callback_query.from_user.id) == 0:
                    sleep(1)
                    await iteration_message.edit_text(f'⏳ Отдых - {seconds} сек.',
                                                      reply_markup=mks.active_training_skip_timer_menu)

                # Если значение проверки = 1, то таймер останавливается
                # и вызывает функцию возвращения значения по умолчанию
                else:
                    db.default_timer(callback_query.from_user.id)
                    break

            await iteration_message.edit_text(f'⌛ Отдых закончен. Приступить к следующему подходу!')
            await exercise_message.edit_reply_markup(mks.active_training_menu)
            await state.update_data(iteration_message = iteration_message)

        # Данное условие означает, что итерация превысила длину строки
        else:

            await callback_query.message.answer('❗ Упражнение закончено!\nКак только будешь готов приступить к следующему, нажми на кнопку!', reply_markup=mks.start_training_menu)

            # Переход к следующей строке
            line_number = data['line_number']
            line_number += 1

            # Обновление данных в хранилище
            await state.update_data(line_number = line_number)
            await exercise_message.delete()

        # Повышение количества итерация и передача его в хранилище
        iteration += 1
        await state.update_data(iteration = iteration)


    ''' 
    Хендлер, срабатывающий при нажатие на кнопку "🛑 Пропустить" во время работы таймера.
    Принцип работы:
        Он улавливает нажатие кнопки "🛑 Пропустить"
        При нажатии на кнопку изменяет значение skip_timer в БД на 1
        Во время работы таймера каждую секунду проверяется значение skip_timer:
            - когда равен 0, таймер продолжает свою работу
            - когда равен 1, таймер останавливается и вызывается функция, возвращающая значение 0     
    '''
    @dp.callback_query_handler(lambda c: c.data == 'skip_timer', state='*')
    async def skip_timer(callback_query: CallbackQuery):
        await db.skip_timer(callback_query.from_user.id)


    @dp.callback_query_handler(lambda c: c.data == 'exit_training', state=Training.active_training)
    async def exit_training(callback_query: CallbackQuery, state: FSMContext):

        await callback_query.message.delete()
        data = await state.get_data()

        try:

           iteration_message = data['iteration_message']
           await iteration_message.delete()

        except:

            pass

        await callback_query.message.answer('Прогресс этой тренировки не сохранится!', reply_markup=mks.training_warning_menu)


    @dp.callback_query_handler(lambda c: c.data == 'continue_training', state='*')
    async def continue_training(callback_query: CallbackQuery, state: FSMContext):

        training_info = db.get_training(callback_query.from_user.id)
        await callback_query.message.delete()

        await start_training(training_info, callback_query, state)


    @dp.callback_query_handler(lambda c: c.data == 'new_training', state='*')
    async def new_training(callback_query: CallbackQuery, state: FSMContext):

        await callback_query.message.delete()

        categories_of_trainings_list = os.listdir(f'{path}/Training/Trainings')
        categories_of_trainings_menu = InlineKeyboardMarkup(row_width=1)

        for category in categories_of_trainings_list:

            category_btn = InlineKeyboardButton(category, callback_data=category)
            categories_of_trainings_menu.add(category_btn)
            await show_categories(dp, category, path)

        categories_of_trainings_menu.add(mks.trainings)

        await callback_query.message.answer('Выберите категорию тренировки',
                                            reply_markup=categories_of_trainings_menu)


async def show_categories(dp, category, path):

    @dp.callback_query_handler(lambda c: c.data == category, state = '*')
    async def categories(callback_query: CallbackQuery, state: FSMContext):

        await callback_query.message.delete()

        trainings_list = os.listdir(f'{path}/Training/Trainings/{category}')
        trainings_list_menu = InlineKeyboardMarkup(row_width=1)

        for training in trainings_list:

            training_btn = InlineKeyboardButton(training, callback_data=training)
            trainings_list_menu.add(training_btn)
            await show_trainings(dp, training, category, path)

        trainings_list_menu.add(mks.trainings)

        await callback_query.message.answer('Выберите тренировку',
                                            reply_markup=trainings_list_menu)


async def show_trainings(dp, training, category, path):

    # Хендлер для каждой тренировки, callback'ом будет название папки, в которой лежат файлы с днями тренировки
    @dp.callback_query_handler(lambda c: c.data == training, state='*')
    async def categories(callback_query: CallbackQuery, state: FSMContext):

        await callback_query.message.delete()

        training_info = ''

        days_list = os.listdir(f'{path}/Training/Trainings/{category}/{training}')
        await state.update_data(category = category, training = training)
        for day in days_list:

            training_info += (f'\n\n<b>День цикла <u>№{day.split(".")[0]}</u></b>\n\n')
            with open(f'{path}/Training/Trainings/{category}/{training}/{day}',  encoding="utf-8") as day_of_training:

                excercises = day_of_training.readlines()

                for exercise in excercises:
                    exercise_info = exercise.split(":")
                    training_info += (f'<b>{exercise_info[0]}</b>, количество подходов - {exercise_info[1]}\n')


        await callback_query.message.answer(f'<b>{training}</b>\n{training_info}',
                                            parse_mode="HTML",
                                            reply_markup=mks.choose_training_menu)


    @dp.callback_query_handler(lambda c: c.data == 'apply_training', state='*')
    async def apply_training(callback_query: CallbackQuery, state: FSMContext):
        data = await state.get_data()
        category = data['category']
        training = data['training']
        db.set_training(callback_query.from_user.id, category, training, '1')

        await callback_query.message.delete()

        await callback_query.message.answer(f'✅ Вы выбрали тренировку - <b>{training}</b>\n',
                                            parse_mode="HTML",
                                            reply_markup=mks.after_creating_training_menu)