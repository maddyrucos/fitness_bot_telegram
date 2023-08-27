from datetime import date
import sqlite3 as sq
import for_admin
import os


os.chdir('Database')
db = sq.connect('fitness.db')
cur = db.cursor()
os.chdir('..')


# Инициализация БД
async def init_db():

    # Создается таблица пользователей
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
    user_id              INTEGER PRIMARY KEY,
    username             TEXT,
    gender               TEXT,
    age                  INTEGER,
    weight               TEXT,
    height               TEXT,
    IMB                  TEXT,
    muscle_weight        TEXT,
    fat_weight           TEXT,
    trainings_count      INTEGER,
    date_of_registration TEXT)''')
    db.commit()

    # Создается таблица тренировок
    cur.execute('''CREATE TABLE IF NOT EXISTS trainings (
    user_id    INTEGER PRIMARY KEY,
    category   TEXT,
    training   TEXT,
    day        INTEGER,
    skip_timer INTEGER DEFAULT (0) )''')
    db.commit()

    # Создается таблица администраторов
    cur.execute("CREATE TABLE IF NOT EXISTS admins(username TEXT PRIMARY KEY)")
    db.commit()


# Создание профиля
async def create_profile(user_id, username):

    # Из БД берется запись с переданным id
    user = cur.execute(f"SELECT 1 FROM users WHERE user_id == '{user_id}'").fetchone()

    # Если записи не найдено, то создается профиль в двух таблицах (users, trainings)
    if not user:

        # В таблицу users вносится id, username и дата регистрации
        cur.execute(f'INSERT INTO users (user_id, username, trainings_count, date_of_registration) VALUES("{user_id}", "{username}", "0", "{date.today()}")')
        db.commit()

        # В таблицу trainings по умолчанию добавляется только id
        cur.execute(f'INSERT INTO trainings (user_id) VALUES("{user_id}")')
        db.commit()


# Получение информации о тренировке из БД
def get_training(user_id):

    # Получение тренировки (пути к файлу) через id
    cur.execute(f'SELECT category, training, day FROM trainings WHERE "user_id" == "{user_id}"')
    training = cur.fetchone()

    return training


# Изменение тренировки в БД
def set_training(user_id, category, training, day):

    # Присвоение пользователю тренировки (пути к файлу)
    cur.execute(f'UPDATE trainings SET "category" = "{category}", "training" = "{training}", "day" = "{day}" WHERE "user_id" == "{user_id}"')
    db.commit()


# Проверка на администратора
async def check_admin(bot, dp, username, user_id):

    # Из БД берется указанный username
    cur.execute(f"SELECT username FROM admins WHERE username == '{username}'")  # берем список админов
    admin = cur.fetchone()

    # Проверка на наличие этого username'а в БД. В случае отсутствия ничего не происходит
    if admin == None:

        pass

    # При наличии данного username'а вызывается функция для администраторов
    else:

        await for_admin.admin(bot, dp, user_id, db)


# Изменение значения в БД для пропуска таймера
async def skip_timer(user_id):

    cur.execute(f'UPDATE trainings SET "skip_timer" = "1" WHERE "user_id" == "{user_id}"')
    db.commit()


# Выставление значения таймера по умолчанию
def default_timer(user_id):

    cur.execute(f'UPDATE trainings SET "skip_timer" = "0" WHERE "user_id" == "{user_id}"')
    db.commit()

# Проверка значения остановки таймера
def check_timer(user_id):

    cur.execute(f'SELECT skip_timer FROM trainings WHERE user_id == "{user_id}"')
    skip_value = cur.fetchone()
    return skip_value[0]


# Обновление количества тренировок с момента регистрации
def update_trainings_count(user_id):

    # Получение из БД текущего значения, увеличение его, внесение нового значения в БД и сохранение
    cur.execute(f'SELECT trainings_count FROM users WHERE user_id == "{user_id}"')
    current_count_of_trainings = int(cur.fetchone()[0]) + 1
    cur.execute(f'UPDATE users SET "trainings_count" = "{current_count_of_trainings}" WHERE "user_id" == "{user_id}"')
    db.commit()


# Получение информации из БД для отображения профиля
def get_profile_info(user_id):

    cur.execute(f'SELECT username, gender, age, weight, height, IMB, muscle_weight, fat_weight, '
                f'trainings_count, date_of_registration FROM users WHERE user_id == "{user_id}"')
    user_info = cur.fetchone()
    return user_info


# Изменение роста в БД
def change_height(user_id, height):

    cur.execute(f'UPDATE users SET "height" = "{height}" WHERE user_id == "{user_id}"')
    db.commit()


# Изменение веса в БД
def change_weight(user_id, weight):
    cur.execute(f'UPDATE users SET "weight" = "{weight}" WHERE user_id == "{user_id}"')
    db.commit()


# Изменение ИМТ
def add_imb(user_id, imb):
    # Добавление ИМТ в БД
    cur.execute(f'UPDATE users SET "IMB" = "{imb}" WHERE "user_id" == "{user_id}"')
    db.commit()


def change_profile(user_id, new_value, position):
    cur.execute(f'UPDATE users SET "{position}" = "{new_value}" WHERE "user_id" == "{user_id}"')
    db.commit()
    return True