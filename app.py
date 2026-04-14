import os
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from threading import Thread
from urllib.parse import urlparse as url_parse
from datetime import datetime
import pytz

from config import Config
from models import db, User, Checkup, JournalEntry
from forms import LoginForm, RegistrationForm, CheckupForm, JournalForm, RequestResetForm, ResetPasswordForm
from utils import (
    SIMPLE_QUESTIONS_MAP, STUDENT_TIPS, SUPPORT_GROUPS_TEXT,
    MEDICAL_DISCLAIMER, simple_checkup_analysis
)

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# === ИНИЦИАЛИЗАЦИЯ ПОЧТЫ ===
mail = Mail(app)

# === КОНТЕКСТНЫЙ ПРОЦЕССОР ДЛЯ ПЕРЕДАЧИ ЧАСОВОГО ПОЯСА В ШАБЛОНЫ ===
@app.context_processor
def inject_timezone():
    return dict(tz=pytz.timezone('Asia/Novosibirsk'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Создание таблиц при первом запуске
with app.app_context():
    db.create_all()

# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ ПОЧТЫ ===
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_reset_email(user):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    token = serializer.dumps(user.email, salt='password-reset-salt')
    msg = Message('Сброс пароля MindSpace',
                  recipients=[user.email])
    link = url_for('reset_token', token=token, _external=True)
    msg.body = f'''Чтобы сбросить пароль, перейдите по ссылке:
{link}

Если вы не запрашивали сброс пароля, проигнорируйте это письмо.
'''
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()

# === МАРШРУТЫ АУТЕНТИФИКАЦИИ ===
@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html', disclaimer=MEDICAL_DISCLAIMER)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Неверное имя пользователя или пароль')
            return redirect(url_for('login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('auth/login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Поздравляем, вы зарегистрированы!')
        return redirect(url_for('login'))
    return render_template('auth/register.html', form=form)

# === МАРШРУТЫ СБРОСА ПАРОЛЯ ===
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)
            flash('Письмо с инструкцией отправлено на ваш email.', 'info')
        else:
            flash('Пользователь с таким email не найден.', 'warning')
        return redirect(url_for('login'))
    return render_template('auth/reset_request.html', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=3600)  # 1 час
    except:
        flash('Ссылка недействительна или устарела.', 'warning')
        return redirect(url_for('reset_request'))
    user = User.query.filter_by(email=email).first_or_404()
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Пароль успешно изменён. Теперь вы можете войти.', 'success')
        return redirect(url_for('login'))
    return render_template('auth/reset_token.html', form=form)

# === ОСНОВНЫЕ МАРШРУТЫ ===
@app.route('/checkup', methods=['GET', 'POST'])
@login_required
def checkup():
    form = CheckupForm()
    if form.validate_on_submit():
        checkup_data = Checkup(
            user_id=current_user.id,
            stress=form.stress.data,
            sleep=form.sleep.data,
            energy=form.energy.data,
            focus=form.focus.data,
            satisfaction=form.satisfaction.data,
            motivation=form.motivation.data,
            social=form.social.data,
            nutrition=form.nutrition.data,
            hopes=form.hopes.data,
            control=form.control.data
        )
        db.session.add(checkup_data)
        db.session.commit()
        return redirect(url_for('result', checkup_id=checkup_data.id))
    return render_template('checkup.html', form=form, questions=SIMPLE_QUESTIONS_MAP)

@app.route('/result/<int:checkup_id>')
@login_required
def result(checkup_id):
    checkup = Checkup.query.get_or_404(checkup_id)
    if checkup.user_id != current_user.id:
        flash('У вас нет доступа к этому результату')
        return redirect(url_for('index'))
    data = {
        'stress': checkup.stress,
        'sleep': checkup.sleep,
        'energy': checkup.energy,
        'focus': checkup.focus,
        'satisfaction': checkup.satisfaction,
        'motivation': checkup.motivation,
        'social': checkup.social,
        'nutrition': checkup.nutrition,
        'hopes': checkup.hopes,
        'control': checkup.control,
        'date': checkup.date.strftime("%d.%m.%Y %H:%M")
    }
    report = simple_checkup_analysis(data)
    return render_template('result.html', 
                           report=report, 
                           checkup=checkup, 
                           date=datetime.now().strftime("%d %B %Y"))
@app.route('/my_state')
@login_required
def my_state():
    latest = Checkup.query.filter_by(user_id=current_user.id).order_by(Checkup.date.desc()).first()
    if not latest:
        flash('Вы ещё не проходили чек-ап')
        return redirect(url_for('checkup'))
    data = {
        'stress': latest.stress,
        'sleep': latest.sleep,
        'energy': latest.energy,
        'focus': latest.focus,
        'satisfaction': latest.satisfaction,
        'motivation': latest.motivation,
        'social': latest.social,
        'nutrition': latest.nutrition,
        'hopes': latest.hopes,
        'control': latest.control,
        'date': latest.date.strftime("%d.%m.%Y %H:%M")
    }
    # Передаём id для кнопки удаления
    return render_template('my_state.html', data=data, questions=SIMPLE_QUESTIONS_MAP, checkup_id=latest.id)

@app.route('/checkups')
@login_required
def checkups_history():
    """История всех чек-апов пользователя"""
    checkups = Checkup.query.filter_by(user_id=current_user.id).order_by(Checkup.date.desc()).all()
    return render_template('checkups_history.html', checkups=checkups, questions=SIMPLE_QUESTIONS_MAP)

@app.route('/checkup/delete/<int:checkup_id>', methods=['POST'])
@login_required
def delete_checkup(checkup_id):
    checkup = Checkup.query.get_or_404(checkup_id)
    if checkup.user_id != current_user.id:
        flash('У вас нет прав на удаление этого чек-апа.', 'danger')
        return redirect(url_for('my_state'))
    db.session.delete(checkup)
    db.session.commit()
    flash('Результат чек-апа удалён.', 'success')
    return redirect(url_for('checkups_history'))

@app.route('/student')
@login_required
def student():
    return render_template('student.html', tips=STUDENT_TIPS)

@app.route('/student/<method>')
@login_required
def student_detail(method):
    tip = STUDENT_TIPS.get(method)
    if not tip:
        flash('Методика не найдена')
        return redirect(url_for('student'))
    return render_template('student.html', tip=tip, method=method)

@app.route('/journal', methods=['GET', 'POST'])
@login_required
def journal():
    form = JournalForm()
    if form.validate_on_submit():
        entry = JournalEntry(user_id=current_user.id, text=form.text.data)
        db.session.add(entry)
        db.session.commit()
        flash('Запись добавлена', 'success')
        return redirect(url_for('journal'))
    entries = JournalEntry.query.filter_by(user_id=current_user.id).order_by(JournalEntry.date.desc()).limit(10).all()
    return render_template('journal.html', form=form, entries=entries)

@app.route('/journal/delete/<int:entry_id>', methods=['POST'])
@login_required
def delete_journal_entry(entry_id):
    entry = JournalEntry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id:
        flash('У вас нет прав на удаление этой записи.', 'danger')
        return redirect(url_for('journal'))
    db.session.delete(entry)
    db.session.commit()
    flash('Запись удалена.', 'success')
    return redirect(url_for('journal'))

@app.route('/breathing')
@login_required
def breathing():
    return render_template('breathing.html')

@app.route('/support')
@login_required
def support():
    return render_template('support.html', text=SUPPORT_GROUPS_TEXT)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
