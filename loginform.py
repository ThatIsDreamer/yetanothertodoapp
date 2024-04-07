from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class RegForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    name = StringField("Имя", validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

class CreateTaskForm(FlaskForm):
    title = StringField("Задача", validators=[DataRequired()])
    tag = SelectField('Выбери тэг', choices=[])
    submit = SubmitField('Добавить задачу')

class CreateTag(FlaskForm):
    title = StringField("Название тэга", validators=[DataRequired()])
    emojiastext = StringField("", validators=[DataRequired()])
    submit = SubmitField('Добавить тэг')
