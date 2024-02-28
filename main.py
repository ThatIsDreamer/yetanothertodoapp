from flask import Flask, render_template, request, session, redirect, flash
from loginform import LoginForm, RegForm
from data import db_session
from data.users import User
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

import string
import random


app = Flask(__name__)

app.config['SECRET_KEY'] = 'ilovecats'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['REMEMBER_COOKIE_DURATION'] = 10



@app.route('/login', methods=['GET', 'POST'])
def login():
    db_sess = db_session.create_session()
    form = LoginForm()
    if form.validate_on_submit():

        if check_password_hash(db_sess.query(User).filter(User.email == form.data["username"]).first().hashed_password, form.data["password"]):
            session["uid"] = db_sess.query(User).filter(User.email == form.data["username"]).first().uid

        else:
            flash('Неправильный логин или пароль!', 'error')


        return redirect('/main')
    return render_template('login.html', form=form)

@app.route('/reg', methods=['GET', 'POST'])
def reg():
    form = RegForm()
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        if not db_sess.query(User).filter(User.email == form.data["username"]).first():
            user = User()
            user.email = form.data["username"]
            user.hashed_password = generate_password_hash(form.data["password"])
            user.name = form.data["name"]
            user.uid = ''.join(random.choices(string.ascii_uppercase +
                                 string.digits + string.ascii_lowercase, k=32))


            db_sess.add(user)
            db_sess.commit()

            return redirect('/main')
        else:
            flash('Пользователь уже существует!', 'error')
    return render_template('reg.html', form=form)



@app.route("/")
def index():
    if "uid" not in session.keys():
        return redirect("/login")
    return redirect("/main")


@app.route("/main")
def main():
    if "uid" not in session.keys():
        return redirect("/login")
    return f'{session["uid"]}'

if __name__ == '__main__':
    db_session.global_init("db/users.sqlite")
    app.run(port=5000, host='127.0.0.1')