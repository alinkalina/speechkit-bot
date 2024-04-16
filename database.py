import sqlite3
from limits import MAX_USERS, MAX_SYMBOLS_FOR_USER


def open_db():
    con = sqlite3.connect('db.sqlite', check_same_thread=False)
    cur = con.cursor()
    return con, cur


def create_tables():
    connection, cursor = open_db()

    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER NOT NULL UNIQUE,
        tg_username TEXT NOT NULL
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS texts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        author_id INTEGER NOT NULL,
        voice TEXT DEFAULT "",
        text TEXT DEFAULT "",
        FOREIGN KEY (author_id) REFERENCES users (id)
    );
    ''')

    cursor.close()
    connection.commit()
    connection.close()


def change_db(sql):
    connection, cursor = open_db()
    cursor.execute(sql)
    cursor.close()
    connection.commit()
    connection.close()


def get_from_db(sql):
    connection, cursor = open_db()
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result


def user_in_db(user_id):
    res = get_from_db(f'SELECT * FROM users WHERE chat_id = {user_id};')
    return res


def add_user(user_id, username):
    if len(get_from_db('SELECT * FROM users')) < MAX_USERS:
        if not user_in_db(user_id):
            change_db(f'INSERT INTO users (chat_id, tg_username) VALUES ({user_id}, "{username}");')
        return True
    return False


def get_username(user_id):
    return get_from_db(f'SELECT tg_username FROM users WHERE chat_id = {user_id};')


def start_text(user_id):
    change_db(f'INSERT INTO texts (author_id) VALUES ((SELECT id FROM users WHERE chat_id = {user_id}));')


def set_voice(user_id, voice):
    change_db(f'UPDATE texts SET voice = "{voice}" '
              f'WHERE author_id = (SELECT id FROM users WHERE chat_id = {user_id}) '
              f'AND text = "";')


def set_text(user_id, text):
    change_db(f'UPDATE texts SET text = "{text}" '
              f'WHERE id = (SELECT MAX(id) FROM texts '
              f'WHERE author_id = (SELECT id FROM users WHERE chat_id = {user_id}));')


def get_voice(user_id):
    return get_from_db(f'SELECT voice FROM texts '
                       f'WHERE author_id = (SELECT id FROM users WHERE chat_id = {user_id}) '
                       f'ORDER BY id DESC LIMIT 1;')


def get_all_user_texts(user_id):
    return get_from_db(f'SELECT text FROM texts WHERE author_id = (SELECT id FROM users WHERE chat_id = {user_id});')


create_tables()
