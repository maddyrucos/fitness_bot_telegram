import sqlite3 as sq
import for_admin
import os


os.chdir('Database')
db = sq.connect('fitness.db')
cur = db.cursor()
os.chdir('..')

async def init_db():

    #Таблица пользователей
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
    user_id          INTEGER PRIMARY KEY,
    username         TEXT,
    gender           TEXT,
    category TEXT,
    training         TEXT,
    day              INTEGER,
    IMB              TEXT)''')
    db.commit()

    #Таблица администраторов
    cur.execute("CREATE TABLE IF NOT EXISTS admins(username TEXT PRIMARY KEY)")  #
    db.commit()

async def create_profile(user_id, username):

    user = cur.execute(f"SELECT 1 FROM users WHERE user_id == '{user_id}'").fetchone()

    if not user:
        cur.execute(f'INSERT INTO users (user_id, username) VALUES("{user_id}", "{username}")')
        db.commit()

def add_imb(user_id, imb):
    # Добавление ИМТ в БД
    cur.execute(f'UPDATE users SET "IMB" = "{imb}" WHERE "user_id" == "{user_id}"')
    db.commit()


def get_training(user_id):
    #Получение тренировки (пути к файлу) через id
    cur.execute(f'SELECT category, training, day FROM users WHERE "user_id" == "{user_id}"')
    training = cur.fetchone()

    return training


def set_training(user_id, category, training, day):

    # Присвоение пользователю тренировки (пути к файлу)
    cur.execute(f'UPDATE users SET "category" = "{category}", "training" = "{training}", "day" = "{day}" WHERE "user_id" == "{user_id}"')
    db.commit()



# Проверка на администратора
async def check_admin(bot, dp, username, user_id):
    cur.execute(f"SELECT username FROM admins WHERE username == '{username}'")  # берем список админов
    admin = cur.fetchone()
    if admin == None:

        pass

    else:

        await for_admin.admin(bot, dp, user_id, db)  # если username есть в списке, то активируется функция админа