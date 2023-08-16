import sqlite3
from datetime import date


def create_tables():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS code_word(id INTEGER PRIMARY KEY AUTOINCREMENT, word text)')
    cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, is_confirmed BOOLEAN)')
    cur.execute('CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT,body TEXT,  created_at DATE, password TEXT)')

    cur.execute('CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY AUTOINCREMENT, note_id INTEGER, comment TEXT,user_id INTEGER,  FOREIGN KEY (note_id) REFERENCES notes(id), FOREIGN KEY (user_id) REFERENCES users(id))')
    cur.execute('CREATE TABLE IF NOT EXISTS reactions (id INTEGER PRIMARY KEY AUTOINCREMENT, note_id INTEGER, reaction TEXT, FOREIGN KEY (note_id) REFERENCES notes(id))')
    conn.commit()
    conn.close()





def get_years():
     conn = sqlite3.connect('database.db')
     cur = conn.cursor()
     cur.execute("SELECT created_at FROM notes")
     results  = cur.fetchall()
     years = []
     [years.append(str(res[0])[:4]) for res in results if str(res[0])[:4] not in years] 
     return sorted(years, reverse=True)


def get_notes(filter: str, value: str):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    if filter == "day":
        cur.execute("SELECT * FROM notes WHERE created_at = ?", (str(value),))
        rows = cur.fetchall()
        return rows
    elif filter == "month":
        cur.execute("SELECT * FROM notes WHERE strftime('%m', created_at) = ?", (str(value),))
        rows = cur.fetchall()
        return rows
    elif filter == "year":
        cur.execute("SELECT * FROM notes WHERE strftime('%Y', created_at) = ?", (str(value),))
        rows = cur.fetchall()
        return rows
    conn.close()
    return None
    

def get_notes_count(filter: str, value: str):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    if filter == "day":
        cur.execute("SELECT COUNT(*) FROM notes WHERE strftime('%d', created_at) = ?", (str(value),))
        count = cur.fetchone()
        return count[0]
    elif filter == "month":
        cur.execute("SELECT COUNT(*) FROM notes WHERE strftime('%m', created_at) = ?", (str(value),))
        count = cur.fetchone()
        return count[0]
    elif filter == "year":
        cur.execute("SELECT COUNT(*) FROM notes WHERE strftime('%Y', created_at) = ?", (str(value),))
        count = cur.fetchone()
        return count[0]
    conn.close()
def get_one_note(id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM notes WHERE id = ?", (id, ))
    results  = cur.fetchone()
    return results

def edit_user_confirm(id_user: int):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute('UPDATE users SET is_confirmed = True WHERE id = ?',(id_user,))
    conn.commit()
    conn.close()





def get_status(id_user):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
     # Выполнение запроса SELECT с использованием параметра
    cur.execute('SELECT is_confirmed FROM users WHERE id = ?', (id_user,))

    # Получение результата запроса
    result = cur.fetchone()

    # Если запись найдена, возвращаем значение is_confirmed
    if result:
        is_confirmed = result[0]
        return is_confirmed

    # Если запись не найдена, возвращаем None или другое значение по умолчанию
    return None


def check_user(id_user: int):
     conn = sqlite3.connect('database.db')
     cur = conn.cursor()

     cur.execute('select * from users where id = ?', (id_user,))
     res = cur.fetchone()
     if res:
          return True
     
     return False


def create_user(id_user: int):
     conn = sqlite3.connect('database.db')
     cur = conn.cursor()

     cur.execute('INSERT INTO users (id, is_confirmed) VALUES (?,?)', (id_user, False, ))
     conn.commit()
     conn.close()

def add_comment(note_id, comment, user_id):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('INSERT INTO comments (note_id, comment, user_id) VALUES (?, ?, ?)', (note_id, comment, user_id))
    connection.commit()
    cursor.close()
    connection.close()


def add_reaction(note_id, reaction):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('INSERT INTO reactions (note_id, reaction) VALUES (?, ?)', (note_id, reaction))
    connection.commit()
    cursor.close()
    connection.close()

def get_comments():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM comments')
    rows = cursor.fetchall()
    return rows
def get_reactions():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM reactions')
    rows = cursor.fetchall()
    return rows




def get_person_comments(user_id):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM comments WHERE user_id = ?', (user_id, ))
    rows = cursor.fetchall()
    return rows



def add_note(title:str, body:str, password:str):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    current_date = date.today()
    cursor.execute('INSERT INTO notes (title, body ,created_at, password) VALUES (?, ?, ?,?)', (title, body, current_date,password, ))
    connection.commit()
    cursor.close()
    connection.close()

def get_users_id():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT (id) FROM users')
    rows = cursor.fetchall()
    return rows