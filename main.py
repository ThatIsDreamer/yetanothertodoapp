from flask import Flask, render_template, request, session, redirect, flash
from loginform import LoginForm, RegForm
from data import db_session
from data.users import User
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
import datetime
import string
import random


app = Flask(__name__)

app.config['SECRET_KEY'] = 'ilovecats'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)

@app.route('/reg', methods=['GET', 'POST'])
def reg():
    form = RegForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('reg.html', title='Регистрация', form=form,
                                   message='такой пользователь уже есть')

        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/main')
    else:
        return render_template('reg.html', form=form)



@app.route("/")
@login_required
def index():
    return redirect("/main")


@app.route("/main")
@login_required
def main():
    return f'{current_user.id}'

if __name__ == '__main__':
    db_session.global_init("db/users.sqlite")
    app.run(port=5000, host='127.0.0.1')