import datetime
import os
import sqlite3

from flask import Flask, render_template, url_for, request, flash, get_flashed_messages, g, abort, session, redirect

from flask_006.flask_database import FlaskDataBase

from werkzeug.security import generate_password_hash, check_password_hash

DATABASE = 'flaskapp.db'
DEBUG = True
SECRET_KEY = 'gheghgj3qhgt4q$#^#$he'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flaskapp.db')))


def create_db():
    """Creates new database from sql file."""
    db = connect_db()
    with app.open_resource('db_schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def connect_db():
    """Returns connention to apps database."""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


url_menu_items = {
    'index': 'Главная',
    'second': 'Вторая страница'
}


@app.route('/')
def index():
    fdb = FlaskDataBase(get_db())
    return render_template(
        'index.html',
        menu_url=fdb.get_menu(),
        posts=fdb.get_posts()
    )


@app.route('/page2')
def second():
    fdb = FlaskDataBase(get_db())

    print(url_for('second'))
    print(url_for('index'))

    return render_template(
        'second.html',
        phone='+79172345678',
        email='myemail@gmail.com',
        current_date=datetime.date.today().strftime('%d.%m.%Y'),
        menu_url=fdb.get_menu()
    )


# int, float, path
@app.route('/user/<username>')
def profile(username):
    return f"<h1>Hello {username}!</h1>"


@app.route('/add_post', methods=["GET", "POST"])
def add_post():
    fdb = FlaskDataBase(get_db())

    if request.method == "POST":
        name = request.form["name"]
        post_content = request.form["post"]
        if len(name) > 5 and len(post_content) > 10:
            res = fdb.add_post(name, post_content)
            if not res:
                flash('Post were not added. Unexpected error', category='error')
            else:
                flash('Success!', category='success')
        else:
            flash('Post name or content too small', category='error')

    return render_template('add_post.html', menu_url=fdb.get_menu())


@app.route('/post/<int:post_id>')
def post_content(post_id):
    fdb = FlaskDataBase(get_db())
    title, content = fdb.get_post_content(post_id)
    if not title:
        abort(404)
    return render_template('post.html', menu_url=fdb.get_menu(), title=title, content=content)


@app.route('/login', methods=['POST', 'GET'])
def login():
    fdb = FlaskDataBase(get_db())
    if request.method == 'GET':
        if not session.get('user'):
            return render_template('login.html', menu_url=fdb.get_menu())
        else:
            return render_template('log_out.html', menu_url=fdb.get_menu())
    elif request.method == 'POST':
        # log_out = True # request.form.get("Log out")
        # if log_out:
        #     session.pop('user', None)
        #     return redirect(url_for('index'))
        email = request.form.get('email')
        password = request.form.get('password')
        if not email:
            flash('Email не указан!', category='unfilled_error')
        else:
            if '@' not in email or '.' not in email:
                flash('Некорректный email!', category='validation_error')
        if not password:
            flash('Пароль не указан!', category='unfilled_error')
        user = fdb.get_user(email)
        if not user:
            flash("Пользователь не зарегистрирован.", category="error")
        else:
            hashpwd = user[0]['password']
            if not check_password_hash(hashpwd, password):
                flash("Неправильный пароль!", category='error')
            else:
                session.permanent = True
                session['user'] = email
                return redirect(url_for('index'))
        print(request)
        print(get_flashed_messages(True))
        return render_template('login.html', menu_url=fdb.get_menu())
    else:
        raise Exception(f'Method {request.method} not allowed')


@app.errorhandler(404)
def page_not_found(error):
    return "<h1>Ooooops! This post does not exist!</h1>"


@app.teardown_appcontext
def close_db(error):
    """Close database connection if it exists."""
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route('/sign_up', methods=['POST', 'GET'])
def sign_up():
    fdb = FlaskDataBase(get_db())

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        user = fdb.get_user(email)
        if user:
            flash("Такой email уже зарегистрирован.", category="error")
        else:
            if not email:
                flash('Email не указан!', category='unfilled_error')
            else:
                if '@' not in email or '.' not in email:
                    flash('Некорректный email!', category='validation_error')
            if len(password) > 8 and not password.isdigit() and not password.isalpha():
                hash_password = generate_password_hash(password)
                res = fdb.add_user(email, hash_password, name)
                if not res:
                    flash("You haven't been signed up.", category='error')
                else:
                    flash('Success!', category='success')
            else:
                flash('Simple password!', category='error')

    return render_template('sign_up.html', menu_url=fdb.get_menu())


if __name__ == '__main__':
    app.run(debug=True)
