from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, NumberRange
from models import User

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Это имя уже занято.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Этот email уже зарегистрирован.')

class CheckupForm(FlaskForm):
    stress = IntegerField('Стресс (1-10)', validators=[DataRequired(), NumberRange(min=1, max=10)])
    sleep = IntegerField('Сон (1-10)', validators=[DataRequired(), NumberRange(min=1, max=10)])
    energy = IntegerField('Энергия (1-10)', validators=[DataRequired(), NumberRange(min=1, max=10)])
    focus = IntegerField('Фокус (1-10)', validators=[DataRequired(), NumberRange(min=1, max=10)])
    satisfaction = IntegerField('Настроение (1-10)', validators=[DataRequired(), NumberRange(min=1, max=10)])
    motivation = IntegerField('Мотивация (1-10)', validators=[DataRequired(), NumberRange(min=1, max=10)])
    social = IntegerField('Социальные связи (1-10)', validators=[DataRequired(), NumberRange(min=1, max=10)])
    nutrition = IntegerField('Питание (1-10)', validators=[DataRequired(), NumberRange(min=1, max=10)])
    hopes = IntegerField('Оптимизм (1-10)', validators=[DataRequired(), NumberRange(min=1, max=10)])
    control = IntegerField('Чувство контроля (1-10)', validators=[DataRequired(), NumberRange(min=1, max=10)])
    submit = SubmitField('Получить анализ')

class JournalForm(FlaskForm):
    text = TextAreaField('Новая запись', validators=[DataRequired()])
    submit = SubmitField('Сохранить')

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Отправить ссылку для сброса')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Новый пароль', validators=[DataRequired()])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Сбросить пароль')