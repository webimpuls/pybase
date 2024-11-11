# ======================================================================================================================
# Инициализация
# ======================================================================================================================
from flask import Flask, render_template, redirect, url_for, request, flash, g
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3

app = Flask(__name__)
app.secret_key = 'CRmD117vA2DFgPdo'
app.config.update(
    TEMPLATES_AUTO_RELOAD = True,
    DEBUG = True
)

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('database.db', check_same_thread=False)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()

with app.app_context():
    sql = get_db()
    cur = sql.cursor()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'page_auth'

#with open('template/main.html', 'r') as file:
#    template = file.read()

# ======================================================================================================================
# Модель пользователя
# ======================================================================================================================
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

    def auth_op(self, op):
        return get_db().cursor().execute("SELECT COUNT(*) FROM role_user INNER JOIN role_op USING(role) WHERE user = ? AND op = (SELECT id FROM rbac_op WHERE name = ?)", (self.id, op)).fetchone()[0]

@login_manager.user_loader
def user_load(user_id):
    user = get_db().cursor().execute("SELECT id, name FROM user WHERE id = ?", ( user_id, )).fetchone()
    if user:
        return User(user[0], user[1])
    return None

# ======================================================================================================================
#   ROUTES
# ======================================================================================================================
@app.route("/auth", methods=['GET', 'POST'])
def page_auth():
    if current_user.is_authenticated:
        return redirect(url_for('page_main'))

    if request.method == 'POST':
        un = request.form.get('username')
        pw = request.form.get('password')
        user = get_db().cursor().execute("SELECT id, name FROM user WHERE name = ? AND pass = ?", (un, pw)).fetchone()
        if user:
            login_user(User(user[0], user[1]))
            return redirect(url_for('page_main'))
        flash('Invalid username or password')
    return render_template('page-auth.html')

# ======================================================================================================================
@app.route("/exit")
@login_required
def page_exit():
    logout_user()
    return redirect(url_for('page_auth'))

# ======================================================================================================================
@app.route("/", methods=['GET'])
def page_index():
    if current_user.is_authenticated:
        return redirect(url_for('page_main'))
    return redirect(url_for('page_auth'))

# ======================================================================================================================
@app.route("/join", methods=['GET', 'POST'])
def page_join():
    if request.method == 'POST':
        un = request.form.get('username')
        pw = request.form.get('password')
        db = get_db()
        c = db.cursor()
        have = c.execute("SELECT COUNT(*) FROM user WHERE name = ?", (un,)).fetchone()[0]
        if have == 0:
            c.execute("INSERT INTO user(deleted, name, pass) VALUES(0, ?, ?)", (un, pw))
            u_id = c.lastrowid
            db.commit()
            if u_id:
                login_user(User(u_id, un))
                return redirect(url_for('page_main'))
            flash('User registration unknown error')
        if have == 1:
            flash('User exists')

    return render_template('page-join.html')
# ======================================================================================================================
# Главная страница с данными (таблицей user)
# ======================================================================================================================
@app.route("/main", methods=['GET', 'POST', 'DELETE'])
@login_required
def page_main():
    # Обязательная проверка аутентификации
    if not current_user.is_authenticated:
        return redirect(url_for('page_auth'))

    # Получение прав пользователя
    op_c = current_user.auth_op('user_c')  # Создание
    op_r = current_user.auth_op('user_r')  # Чтение
    op_u = current_user.auth_op('user_u')  # Обновление
    op_d = current_user.auth_op('user_d')  # Удаление

    db = get_db()
    c = db.cursor()

    if request.method == 'POST':
        op = request.form.get('op')

        # Создание записи
        if op_c and op == 'create':
            un = request.form.get('username')
            pw = request.form.get('password')
            c.execute("INSERT INTO user(deleted, name, pass) VALUES(0, ?, ?)", (un, pw))
            db.commit()

        # Обновление записи
        if op_u and op == 'update':
            id = request.form.get('id')
            un = request.form.get('username')
            pw = request.form.get('password')
            db.cursor().execute("UPDATE user SET name = ?, pass = ? WHERE id = ?", (un, pw, id))
            db.commit()

        # Удаление записи (пометка deleted)
        if op_d and op == 'delete':
            id = request.form.get('id')
            db.cursor().execute("UPDATE user SET deleted = 1 WHERE id = ?", (id,))
            db.commit()

        return redirect(url_for('page_main'))

    list = []
    if op_r:
        list = get_db().cursor().execute("SELECT id, name, pass FROM user WHERE deleted = 0").fetchall()

    return render_template('page-main.html', list=list, op_c=op_c, op_r=op_r, op_u=op_u, op_d=op_d)

