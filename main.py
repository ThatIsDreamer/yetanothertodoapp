from flask import Flask, render_template, request, session, redirect, flash, abort
from loginform import LoginForm, RegForm, CreateTaskForm
from data import db_session
from data.users import User
from data.tasks import Task
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from datetime import datetime, timedelta, date
from blueprint import tasks_api




app = Flask(__name__)

app.config['SECRET_KEY'] = 'ilovecats'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=365)


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


@app.route("/addtask", methods=['GET', 'POST'])
@login_required
def create_task():
    form = CreateTaskForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        task = Task()
        task.task_name = form.title.data
        task.status = False
        task.date = date.today()
        current_user.tasks.append(task)
        db_sess.merge(current_user)
        db_sess.commit()
        print(current_user.tasks)
        return redirect('/')
    return render_template('createtask.html', title='Добавить задачу', form=form)


@app.route("/main")
@login_required
def redirecttomain():
    now = datetime.now()
    return redirect(f"main/{now.strftime('%D').replace('/', '-')}")

@app.route("/main/<date>")
@login_required
def main(date):
    db_sess = db_session.create_session()

    date = datetime.strptime(date, '%m-%d-%y')

    tasks = db_sess.query(Task).filter(Task.user == current_user, Task.date==date)

    now = datetime.now()

    weekday = now.weekday()

    start_of_week = now - timedelta(days=weekday)

    end_of_week = start_of_week + timedelta(days=6)

    current_week_dates = [(start_of_week + timedelta(days=i)).date() for i in range(7)]

    if date != now:
        return render_template('main.html', title="TO-DO", tasks=tasks, current_week_dates=current_week_dates, now=date, actual=now)
    else:
        return render_template('main.html', title="TO-DO", tasks=tasks, current_week_dates=current_week_dates, now=now, actual=now)



@app.route("/delete/<int:id>")
@login_required
def deletetask(id):
    db_sess = db_session.create_session()
    task = db_sess.query(Task).filter(Task.id == id, Task.user == current_user).first()
    if task:
        db_sess.delete(task)
        db_sess.commit()
    else:
        abort(404)
    return redirect("/")

if __name__ == '__main__':
    db_session.global_init("db/users.sqlite")
    app.run(port=5000, host='127.0.0.1')