import sqlite3

sql = sqlite3.connect('database.db', check_same_thread=False)
sql.row_factory = sqlite3.Row
cur = sql.cursor()

def db_inst():
    # User
    cur.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY,
            deleted INTEGER,
            name TEXT,
            pass TEXT
        )
    ''')
    # Role
    cur.execute('''
        CREATE TABLE IF NOT EXISTS role (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
    ''')
    # Role members
    cur.execute('''
        CREATE TABLE IF NOT EXISTS role_user (
            role INTEGER,
            user INTEGER
        )
    ''')
    # RBAC operations
    cur.execute('''
        CREATE TABLE IF NOT EXISTS rbac_op (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
    ''')
    # Role operations
    cur.execute('''
        CREATE TABLE IF NOT EXISTS role_op (
            role INTEGER,
            op INTEGER
        )
    ''')
    # Role operations

    cur.execute("INSERT INTO user (id, deleted, name, pass) VALUES (1, 0, ?, ?)", ('admin', '123'))
    cur.execute("INSERT INTO user (id, deleted, name, pass) VALUES (2, 0, ?, ?)", ('manager', '123'))
    cur.execute("INSERT INTO user (id, deleted, name, pass) VALUES (3, 0, ?, ?)", ('test', '123'))

    cur.execute("INSERT INTO role (id, name) VALUES (1, ?)", ("Администратор",))
    cur.execute("INSERT INTO role (id, name) VALUES (2, ?)", ("Менеджер",))
    cur.execute("INSERT INTO role (id, name) VALUES (3, ?)", ("Тест",))

    cur.execute("INSERT INTO rbac_op (id, name) VALUES (1, ?)", ("user_c",))
    cur.execute("INSERT INTO rbac_op (id, name) VALUES (2, ?)", ("user_r",))
    cur.execute("INSERT INTO rbac_op (id, name) VALUES (3, ?)", ("user_u",))
    cur.execute("INSERT INTO rbac_op (id, name) VALUES (4, ?)", ("user_d",))

    cur.execute("INSERT INTO role_user (role, user) VALUES (1, 1)")
    cur.execute("INSERT INTO role_user (role, user) VALUES (2, 2)")
    cur.execute("INSERT INTO role_user (role, user) VALUES (3, 3)")

    cur.execute("INSERT INTO role_op (role, op) VALUES (1, 1), (1, 2), (1, 3), (1, 4)")  # crud
    cur.execute("INSERT INTO role_op (role, op) VALUES (2, 1), (2, 2), (2, 3)")          #  r
    cur.execute("INSERT INTO role_op (role, op) VALUES (3, 1)")                          # cru

    sql.commit()


db_inst()

sql.close()
