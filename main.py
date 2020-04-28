from data import db_session
from data.users import User
from data.games import Game
from flask import Flask, request, render_template, redirect, url_for
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed

from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, FileField
from wtforms.validators import DataRequired

from flask_ngrok import run_with_ngrok
from flask_login import LoginManager, login_required, logout_user, login_user, current_user
from werkzeug.utils import secure_filename
import os


ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static', 'img')
app = Flask(__name__)
run_with_ngrok(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db_session.global_init('db/db.sqlite')

login_manager = LoginManager()
login_manager.init_app(app)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


class LoginForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    email = StringField('Login / email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    repeat_password = PasswordField('Repeat password', validators=[DataRequired()])
    username = StringField('username', validators=[DataRequired()])
    submit = SubmitField('Submit')


class UploadForm(FlaskForm):
    file = FileField()


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/')
def main_page():
    session = db_session.create_session()
    games = session.query(Game)
    return render_template("main_page.html", current_user=current_user, games=games)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form, current_user=current_user)
    return render_template('login.html', title='Авторизация', form=form, current_user=current_user)


@app.route('/register', methods=["GET", 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.repeat_password.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают", current_user=current_user)
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть", current_user=current_user)
        user = User(
            email=form.email.data,
            username=form.username.data,
            hashed_password=form.password.data,
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        login_user(user)
        return redirect("/")
    return render_template('register.html', title='Регистрация', form=form, current_user=current_user)

@app.route('/games/<gameid>')
def game(gameid):
    session = db_session.create_session()
    game = session.query(Game).filter(Game.id == gameid).first()
    print(game.name)
    return render_template('game_page.html', current_user=current_user, game=game)


@app.route("/delete_all_users")
def delete_all():
    session = db_session.create_session()
    session.query(User).delete()
    session.commit()
    return redirect("/")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/user', methods=["GET", 'POST'])
@login_required
def user_page():
    form = UploadForm()
    if form.validate_on_submit():
        filename = secure_filename(form.file.data.filename)
        form.file.data.save(os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id) + "." + filename.split(".")[-1]))
        session = db_session.create_session()
        user = session.query(User).filter(User.id == current_user.id).first()
        user.image = "/static/img/" + str(user.id) + "." + filename.split(".")[-1]
        session.commit()
    return render_template("user.html", user=current_user, form=form)

@app.route("/user/change_photo", methods=["GET", 'POST'])
def change_photo():
    form = UploadForm()
    if form.validate_on_submit():
        filename = secure_filename(form.file.data.filename)
        form.file.data.save(
            os.path.join(app.config['UPLOAD_FOLDER'], str(current_user.id) + "." + filename.split(".")[-1]))
        session = db_session.create_session()
        user = session.query(User).filter(User.id == current_user.id).first()
        user.image = "/static/img/" + str(user.id) + "." + filename.split(".")[-1]
        session.commit()
        return redirect("/user")
    return render_template("user_change.html", user=current_user, form=form)


if __name__ == '__main__':
    app.run()