from flask import Flask, render_template, request, session, redirect, flash, abort
from loginform import LoginForm, RegForm, CreateTaskForm, CreateTag
from data import db_session
from data.users import User
from data.tasks import Task
from data.tags import Tags
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import Resource, Api
from blueprint.tasks_api import TaskApi
from datetime import datetime, timedelta, date
from sqlalchemy.orm import make_transient



app = Flask(__name__)
api = Api(app)
api.add_resource(TaskApi, '/api/toggle/<id>')


app.config['SECRET_KEY'] = 'ilovecats'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=365)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


db_session.global_init("db/users.sqlite")

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

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route("/")
@login_required
def index():
    return redirect("/main")


@app.route("/addtask/<seldate>", methods=['GET', 'POST'])
@login_required
def create_task(seldate):
    form = CreateTaskForm()
    db_sess = db_session.create_session()
    user_tags = db_sess.query(Tags).filter(Tags.user == current_user).all()
    print(user_tags)
    form.tag.choices = [(tag.id, [tag.tag_name, tag.emoji]) for tag in user_tags]
    form.tag.choices.insert(0, (None, ["Нет", ":X:"]))
    if form.validate_on_submit():
        task = Task()
        task.task_name = form.title.data
        task.status = False
        task.date = datetime.strptime(seldate, '%m-%d-%y')

        if form.tag.data:
            tag = db_sess.query(Tags).filter(Tags.id == form.tag.data).first()
            task.tag_id = tag.id if tag else None
        else:
            task.tag = None

        db_sess.add(task)

        task.user_id = current_user.id

        db_sess.commit()

        return redirect(f'/main/{seldate}')
    return render_template('createtask.html', title='Добавить задачу', form=form)


@app.route("/createtag", methods=['GET', 'POST'])
@login_required
def createTag():
    form = CreateTag()
    if form.validate_on_submit():
        print(form.emojiastext.data, form.title.data)
        db_sess = db_session.create_session()
        tag = Tags()
        tag.emoji = form.emojiastext.data
        tag.tag_name = form.title.data
        current_user.tags.append(tag)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/main')
    return render_template('createtag.html', title='Добавить тэг', form=form)


@app.route("/main")
@login_required
def redirecttomain():
    now = datetime.now()
    return redirect(f"main/{now.strftime('%D').replace('/', '-')}")

@app.route("/main/<date>")
@login_required
def main(date):
    db_sess = db_session.create_session()


    if current_user.is_authenticated:
        make_transient(current_user)
        db_sess.merge(current_user)

    date = datetime.strptime(date, '%m-%d-%y')

    tasks = db_sess.query(Task).filter(Task.user == current_user, Task.date==date)

    now = datetime.now()

    weekday = now.weekday()

    start_of_week = now - timedelta(days=weekday)

    end_of_week = start_of_week + timedelta(days=6)

    current_week_dates = [(start_of_week + timedelta(days=i)).date() for i in range(7)]


    if date != now:
        return render_template('main.html', title="TO-DO", tasks=list(tasks), current_week_dates=current_week_dates, now=date, actual=now)
    else:
        return render_template('main.html', title="TO-DO", tasks=list(tasks), current_week_dates=current_week_dates, now=now, actual=now)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id: int):
    db_sess = db_session.create_session()
    form = CreateTaskForm()
    user_tags = db_sess.query(Tags).filter(Tags.user == current_user).all()
    print(user_tags)
    form.tag.choices = [(tag.id, [tag.tag_name, tag.emoji]) for tag in user_tags]
    form.tag.choices.insert(0, (None, ["Нет", ":X:"]))

    if request.method == 'GET':
        db_sess = db_session.create_session()
        task: Task = db_sess.query(Task).filter(Task.id == id, Task.user == current_user).first()
        if task:
            form.title.data = task.task_name
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        task: Task = db_sess.query(Task).filter(Task.id == id, Task.user == current_user).first()
        if task:
            task.task_name = form.title.data
            if form.tag.data:
                tag = db_sess.query(Tags).filter(Tags.id == form.tag.data).first()
                task.tag_id = tag.id if tag else None
            else:
                task.tag = None

            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('createtask.html', title='Редактировать задачу', form=form)



    

@app.route("/delete/<int:id>/<redirectto>")
@login_required
def deletetask(id, redirectto):
    db_sess = db_session.create_session()
    task = db_sess.query(Task).filter(Task.id == id, Task.user == current_user).first()
    if task:
        db_sess.delete(task)
        db_sess.commit()
    else:
        abort(404)
    return redirect(f"/main/{redirectto}")

@app.route("/deletetag/<int:id>/")
@login_required
def deletetag(id):
    db_sess = db_session.create_session()
    tag = db_sess.query(Tags).filter(Tags.id == id, Tags.user == current_user).first()
    if tag:
        db_sess.delete(tag)
        db_sess.commit()
    else:
        abort(404)
    return redirect(f"/edittags")

@app.route("/edittags")
@login_required
def edittags():
    db_sess = db_session.create_session()
    user_tags = db_sess.query(Tags).filter(Tags.user == current_user).all()
    return render_template("edittags.html", tags=user_tags, tag_count=len(user_tags))


@app.route("/stats")
@login_required
def profile_stats():
    db_sess = db_session.create_session()

    total_tasks = db_sess.query(Task).filter(Task.user == current_user).count()

    completed_tasks = db_sess.query(Task).filter(Task.user == current_user, Task.status == True).count()

    pending_tasks = total_tasks - completed_tasks

    now = datetime.now()
    start_of_week = now - timedelta(days=now.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    completed_this_week = db_sess.query(Task).filter(
        Task.user == current_user,
        Task.status == True,
        Task.date >= start_of_week,
        Task.date <= end_of_week
    ).count()

    return render_template('stats.html',
                           total_tasks=total_tasks,
                           completed_tasks=completed_tasks,
                           pending_tasks=pending_tasks,
                           completed_this_week=completed_this_week)


if __name__ == '__main__':
    #db_session.global_init("db/users.sqlite")
    app.run(port=5000, host='127.0.0.1')