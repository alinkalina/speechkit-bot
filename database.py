import sqlite3
from limits import MAX_USERS, SECONDS_IN_BLOCK


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

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS audio(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        author_id INTEGER NOT NULL,
        blocks INTEGER DEFAULT 0,
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
    if not user_in_db(user_id):
        if len(get_from_db('SELECT * FROM users')) < MAX_USERS:
            change_db(f'INSERT INTO users (chat_id, tg_username) VALUES ({user_id}, "{username}");')
        else:
            return False
    return True


def get_username(user_id):
    return get_from_db(f'SELECT tg_username FROM users WHERE chat_id = {user_id};')


def get_id_by_chat_id(user_id):
    return get_from_db(f'SELECT id FROM users WHERE chat_id = {user_id};')[0][0]


def start_tts_text(user_id):
    change_db(f'INSERT INTO texts (author_id) VALUES ({get_id_by_chat_id(user_id)});')


def set_voice(user_id, voice):
    change_db(f'UPDATE texts SET voice = "{voice}" WHERE author_id = {get_id_by_chat_id(user_id)} AND text = "";')


def set_text(user_id, text):
    change_db(f'UPDATE texts SET text = "{text}" '
              f'WHERE id = (SELECT MAX(id) FROM texts WHERE author_id = {get_id_by_chat_id(user_id)});')


def get_voice(user_id):
    return get_from_db(f'SELECT voice FROM texts WHERE author_id = {get_id_by_chat_id(user_id)} '
                       f'ORDER BY id DESC LIMIT 1;')


def get_all_user_texts(user_id):
    return get_from_db(f'SELECT text FROM texts WHERE author_id = {get_id_by_chat_id(user_id)};')


def start_stt_text(user_id):
    change_db(f'INSERT INTO audio (author_id) VALUES ({get_id_by_chat_id(user_id)});')


def set_blocks(user_id, duration):
    blocks = (duration // SECONDS_IN_BLOCK) + 1
    change_db(f'UPDATE audio SET blocks = {blocks} '
              f'WHERE id = (SELECT MAX(id) FROM audio WHERE author_id = {get_id_by_chat_id(user_id)});')


def get_user_blocks(user_id):
    return get_from_db(f'SELECT blocks FROM audio WHERE author_id = {get_id_by_chat_id(user_id)};')


create_tables()
